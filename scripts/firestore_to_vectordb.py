import os
from typing import List, Dict, Any
from google.cloud import firestore
from openai import OpenAI
import chromadb
from sentence_transformers import SentenceTransformer 


class FirestoreToVectorDB:
    def __init__(self, persist_dir: str = "./chroma_db") -> None:  # Remove openai_key parameter
        # Firestore client
        print("Initializing Firestore client...")
        self.db: firestore.Client = firestore.Client()
        print("Firestore client initialized.")
        # Local embedding model
        print("Loading local embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # Free, local model
        print("Local embedding model loaded.")
        # Chroma client
        print("Initializing ChromaDB client...")
        self.client_chroma: chromadb.Client = chromadb.PersistentClient(path=persist_dir)
        print("ChromaDB client initialized.")
        # Create or get collection
        print("Getting or creating ChromaDB collection...")
        self.collection = self.client_chroma.get_or_create_collection("procounsel_colleges")
        print("ChromaDB collection ready.")

    def get_all_colleges(self) -> List[str]:
        """
        Dynamically discover all college document IDs by querying the 'data' collection group
        and extracting parent document IDs from the paths.
        """
        # Use collection group query to find all 'data' subcollections
        data_docs = self.db.collection_group("data").limit(1).stream()
        
        colleges = set()
        for doc in data_docs:
            # Extract college ID from document path
            # Path format: collegeScrape/{college_id}/data/{doc_id}
            path_segments = doc.reference.path.split('/')
            if len(path_segments) >= 2 and path_segments[0] == "collegeScrape":
                college_id = path_segments[1]
                colleges.add(college_id)
        
        # Alternative method: Get unique parent documents from all data subcollections
        if not colleges:
            all_data_docs = self.db.collection_group("data").stream()
            for doc in all_data_docs:
                path_segments = doc.reference.path.split('/')
                if len(path_segments) >= 2 and path_segments[0] == "collegeScrape":
                    college_id = path_segments[1]
                    colleges.add(college_id)
                    
                    # Break after finding a few to avoid processing all documents
                    if len(colleges) >= 10:
                        break
        print("Found the following colleges:", colleges)  # DEBUG
        return list(colleges)

    def get_all_json_docs(self, college_doc: str) -> Dict[str, Dict[str, Any]]:
        """
        Return all JSON docs under /collegeScrape/{college_doc}/data/*
        """
        collection_ref = self.db.collection("collegeScrape").document(college_doc).collection("data")
        docs = collection_ref.stream()
        
        data: Dict[str, Dict[str, Any]] = {}
        
        for doc in docs:
            doc_data = doc.to_dict()
            if doc_data:  # Only add non-empty documents
                data[doc.id] = doc_data
        
        print(f"  Retrieved {len(data)} documents for {college_doc}")  # DEBUG
        return data

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks: List[str] = []
        start = 0
        
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk = " ".join(words[start:end])
            if chunk.strip():  # Only add non-empty chunks
                chunks.append(chunk)
            start += chunk_size - overlap
            
        print("Chunking done, total chunks:", len(chunks))  # DEBUG
        return chunks

    # def embed_text(self, text: str) -> List[float]:
    #     """Generate embedding vector using OpenAI"""
    #     response = self.client.embeddings.create(
    #         input=text,
    #         model="text-embedding-3-small"
    #     )
    #     return response.data[0].embedding
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding vector using local Sentence Transformers"""
        embedding = self.embedding_model.encode(text)

        print("Embedding generated, length:", len(embedding))  # DEBUG
        return embedding.tolist() 

    def save_to_vector_db(self, college_name: str) -> None:
        """Fetch all JSONs for a college and store chunks in ChromaDB"""
        docs = self.get_all_json_docs(college_name)
        print(f"  Found {len(docs)} documents for {college_name}")  # DEBUG
        
        if not docs:
            return
        
        total_chunks_added = 0
        
        for doc_id, content in docs.items():
            # Handle different possible content fields
            text_content = ""
            
            # Try different ways to extract text content
            if isinstance(content, dict):
                # Look for common text fields
                for field in ["content", "text", "description", "data", "html_content"]:
                    if field in content:
                        text_content = str(content[field])
                        break
                
                # If no specific text field, convert entire dict to string
                if not text_content.strip():
                    text_content = str(content)
            else:
                text_content = str(content)

            print(f"  Doc {doc_id}: {len(text_content)} chars")  # DEBUG

            if not text_content.strip() or len(text_content) < 10:
                print(f"  Skipping {doc_id} - too short")  # DEBUG
                continue

            try:
                chunks: List[str] = self.chunk_text(text_content)
                if not chunks:
                    print(f"  No chunks created for {doc_id}")  # DEBUG
                    continue
                    
                print(f"  Creating {len(chunks)} chunks for {doc_id}")  # DEBUG
                embeddings: List[List[float]] = [self.embed_text(chunk) for chunk in chunks]
                ids: List[str] = [f"{college_name}_{doc_id}_{i}" for i in range(len(chunks))]
                metadatas: List[Dict[str, str]] = [
                    {
                        "college": college_name, 
                        "source": doc_id,
                        "chunk_index": str(i),
                        "total_chunks": str(len(chunks))
                    } 
                    for i in range(len(chunks))
                ]

                # Add to ChromaDB
                self.collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    documents=chunks,
                    metadatas=metadatas
                )
                
                total_chunks_added += len(chunks)
                print(f"  Added {len(chunks)} vectors for {doc_id}")  # DEBUG
                
            except Exception as e:
                print(f"  Error processing {doc_id}: {e}")  # DEBUG
                continue
        
        print(f"  Total chunks added for {college_name}: {total_chunks_added}")  # DEBUG


    def run(self) -> None:
        """Iterate over all colleges in Firestore and save to vector DB"""
        colleges = self.get_all_colleges()
        
        if not colleges:
            return
        
        print(f"Processing {len(colleges)} colleges for vector database...")
        
        successful = 0
        failed = 0
        
        for college_name in colleges:
            try:
                self.save_to_vector_db(college_name)
                successful += 1
            except Exception as e:
                failed += 1
                continue
        
        total_vectors = self.collection.count()
        print(f"Completed: {successful} successful, {failed} failed, {total_vectors} total vectors stored")
