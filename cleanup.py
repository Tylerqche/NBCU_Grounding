from dotenv import load_dotenv
load_dotenv()

from gen_ai_hub.document_grounding.clients.vector_api_client import VectorAPIClient

vector_client = VectorAPIClient()


def delete_all_documents(collection_id: str):
    documents = vector_client.get_documents(collection_id=collection_id)
    for doc in documents.resources:
        vector_client.delete_document(collection_id=collection_id, document_id=doc.id)
        print(f"Deleted document: {doc.id}")
    print(f"Done — all documents deleted from collection {collection_id}\n")

def delete_all_collections():
    collections = vector_client.get_collections()
    for c in collections.resources:
        vector_client.delete_collection(collection_id=c.id)
        print(f"Deleted collection: {c.id} ({c.title})")
    print("Done — all collections deleted\n")

if __name__ == "__main__":
    delete_all_documents(collection_id="c13373b9-202c-44e4-8e7c-0e5eec409ee9")
    #delete_all_collections()
    pass