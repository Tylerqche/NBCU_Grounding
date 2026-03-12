from dotenv import load_dotenv

# API Information gen_ai_hub 
# https://help.sap.com/doc/generative-ai-hub-sdk/CLOUD/en-US/_api_doc/gen_ai_hub.document_grounding.clients.html

load_dotenv()

from gen_ai_hub.proxy.native.openai import chat
from gen_ai_hub.document_grounding.clients.vector_api_client import VectorAPIClient
from gen_ai_hub.document_grounding.models.vector import (
    CollectionCreateRequest,
    EmbeddingConfig,
    DocumentsCreateRequest,
    BaseDocument,
    TextOnlyBaseChunk,
    VectorKeyValueListPair,
)
from gen_ai_hub.document_grounding.clients.retrieval_api_client import RetrievalAPIClient
from gen_ai_hub.document_grounding.models.retrieval import (
    RetrievalSearchInput,
    RetrievalSearchFilter,
    RetrievalSearchConfiguration,
    RetrievalSearchResults,
)

vector_client = VectorAPIClient()
retrieval_client = RetrievalAPIClient()


def test_llm_connection():
    response = chat.completions.create(
        model_name="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say 'Connection Successful!'"}]
    )
    print(f"LLM check: {response.choices[0].message.content}\n")


def get_or_create_collection():
    collections = vector_client.get_collections()
    existing = next((c for c in collections.resources if c.title == "my_poc_collection"), None)

    if existing:
        print(f"Reusing existing collection id: {existing.id}\n")
        return existing.id

    request = CollectionCreateRequest(
        title="my_poc_collection",
        embeddingConfig=EmbeddingConfig(modelName="text-embedding-3-large"),
        metadata=[]
    )
    vector_client.create_collection(collection_request=request)
    collection_id = vector_client.get_collections().resources[-1].id
    print(f"Collection created id: {collection_id}\n")
    return collection_id


def add_documents(collection_id: str):
    # Check if documents already exist — skip if so
    existing = vector_client.get_documents(collection_id=collection_id)
    if existing.resources:
        print(f"Documents already exist ({len(existing.resources)} found) — skipping insert\n")
        return

    request = DocumentsCreateRequest(
        documents=[
            BaseDocument(
                metadata=[
                    VectorKeyValueListPair(key="source",   value=["internal_wiki"]),
                    VectorKeyValueListPair(key="language", value=["en"]),
                    VectorKeyValueListPair(key="topic",    value=["SAP AI Core"]),
                ],
                chunks=[
                    TextOnlyBaseChunk(
                        content=(
                            "SAP AI Core is a service in SAP BTP that lets you train "
                            "and deploy AI models at scale within the SAP ecosystem."
                        ),
                        metadata=[
                            VectorKeyValueListPair(key="doc_id",  value=["doc_001"]),
                            VectorKeyValueListPair(key="section", value=["overview"]),
                        ]
                    )
                ]
            ),
            BaseDocument(
                metadata=[
                    VectorKeyValueListPair(key="source",   value=["product_docs"]),
                    VectorKeyValueListPair(key="language", value=["en"]),
                    VectorKeyValueListPair(key="topic",    value=["Generative AI Hub"]),
                ],
                chunks=[
                    TextOnlyBaseChunk(
                        content=(
                            "The SAP Generative AI Hub provides a unified API to access "
                            "large language models such as GPT-4o through SAP AI Core."
                        ),
                        metadata=[
                            VectorKeyValueListPair(key="doc_id",  value=["doc_002"]),
                            VectorKeyValueListPair(key="section", value=["overview"]),
                        ]
                    )
                ]
            ),
            # Irrelevant document — should NOT appear in AI/tech searches
            BaseDocument(
                metadata=[
                    VectorKeyValueListPair(key="source",   value=["recipe_blog"]),
                    VectorKeyValueListPair(key="language", value=["en"]),
                    VectorKeyValueListPair(key="topic",    value=["cooking"]),
                ],
                chunks=[
                    TextOnlyBaseChunk(
                        content=(
                            "To make a classic spaghetti carbonara, cook pasta until al dente, "
                            "then mix with eggs, pecorino cheese, pancetta, and black pepper."
                        ),
                        metadata=[
                            VectorKeyValueListPair(key="doc_id",  value=["doc_003"]),
                            VectorKeyValueListPair(key="section", value=["recipe"]),
                        ]
                    )
                ]
            ),
        ]
    )

    result = vector_client.create_documents(collection_id=collection_id, request=request)
    print(f"Documents created: {result}\n")


def search_documents(collection_id: str, query: str):
    search_input = RetrievalSearchInput(
        query=query,
        filters=[
            RetrievalSearchFilter(
                id="my-retrieval-filter",
                dataRepositoryType="vector",
                dataRepositories=[collection_id],
                searchConfiguration=RetrievalSearchConfiguration(
                    maxChunkCount=1
                )
            )
        ]
    )

    results: RetrievalSearchResults = retrieval_client.search(search_input=search_input)
    
    print(f"Retrieval Search Results for: '{query}'")

    for filter_result in results.results:
        if hasattr(filter_result, 'results'):
            for repo_result in filter_result.results:
                doc_repo = repo_result.dataRepository               
                for doc in doc_repo.documents:
                    for chunk in doc.chunks:
                        print(f"\n CONTENT : {chunk.content}")
                        print(f" METADATA: {chunk.metadata}")
        else:
            print(f"Error in filter {filter_result.filterId}: {filter_result.error.message}")
    print("\n")

if __name__ == "__main__":
    test_llm_connection()

    collection_id = get_or_create_collection()
    add_documents(collection_id)
    # Three different queries to show filtering is working correctly, only first most relevant document should return
    search_documents(collection_id, query="Cooking recipes with eggs and cheese.")
    search_documents(collection_id, query="What is SAP AI Core?")
    search_documents(collection_id, query="Give me an overview of the SAP Generative AI Hub.")