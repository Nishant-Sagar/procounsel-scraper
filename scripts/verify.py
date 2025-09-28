# import chromadb
# client = chromadb.PersistentClient(path="./chroma_db")
# collection = client.get_collection("procounsel_colleges")

# results = collection.query(
#     query_texts=["admission process IIT Madras"],
#     n_results=3
# )
# print(results)

# from google.cloud import firestore
# import os

# # Make sure GOOGLE_APPLICATION_CREDENTIALS points to your service account JSON
# # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/path/to/serviceAccount.json"

# def test_firestore_connection():
#     try:
#         db = firestore.Client()
#         print("✅ Connected to Firestore successfully!")

#         collection_name = "collegeScrape"
#         colleges = list(db.collection(collection_name).stream())
#         print(f"Found {len(colleges)} colleges in '{collection_name}' collection:")

#         for college in colleges:
#             print(f" - College document ID: {college.id}")
#             # Optionally list subcollection data
#             subcollection_ref = db.collection(collection_name).document(college.id).collections()
#             for subcol in subcollection_ref:
#                 print(f"   Subcollection: {subcol.id}")
#                 for doc in subcol.stream():
#                     print(f"     Document: {doc.id}")

#     except Exception as e:
#         print("❌ Error connecting to Firestore:", e)

# if __name__ == "__main__":
#     test_firestore_connection()


from google.cloud import firestore

db = firestore.Client()

def check_subcollections(collection_path, doc_id):
    """Check if a document has any subcollections"""
    doc_ref = db.collection(collection_path).document(doc_id)
    
    # List all subcollections
    subcollections = doc_ref.collections()
    
    print(f"Subcollections for {doc_id}:")
    for subcoll in subcollections:
        print(f"  - {subcoll.id}")
        # Get documents from subcollection
        subdocs = list(subcoll.stream())
        print(f"    Documents: {len(subdocs)}")
        for subdoc in subdocs:
            print(f"      * {subdoc.id}")

# Check your specific documents
doc_ids = [
    "IIT_MADRAS_INDIAN_INSTITUTE_OF_TECHNOLOGY_IITM_CHENNAI",
    "VELLORE_INSTITUTE_OF_TECHNOLOGY_VIT_UNIVERSITY_VELLORE"
]

for doc_id in doc_ids:
    check_subcollections("collegeScrape", doc_id)
