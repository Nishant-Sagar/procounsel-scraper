from firestore_to_vectordb import FirestoreToVectorDB

if __name__ == "__main__":
    try:
        vectorizer = FirestoreToVectorDB(persist_dir="./chroma_db")
        vectorizer.run()
        
    except Exception as e:
        print(f"Error: {e}")