from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter,FieldCondition,MatchValue
from app.embeddings import get_embedding_model
from app.config import QDRANT_URL,QDRANT_API_KEY,QDRANT_COLLECTION_NAME

def store_documents(chunks, file_path) -> dict:
    client = QdrantClient(host=QDRANT_URL, api_key=QDRANT_API_KEY)

    records = []

    if client.collection_exists(QDRANT_COLLECTION_NAME):
        scroll_filter = Filter(
            must=[
                FieldCondition(
                    key="metadata.source",
                    match=MatchValue(value=file_path)
                )
            ]
        )
        records, _ = client.scroll(
        collection_name=QDRANT_COLLECTION_NAME,
        scroll_filter=scroll_filter,
        limit=1,
        with_payload=True
    )

    if records:
        return {"status": "skipped", "message": "Document already exists"}

    vector_db = QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=get_embedding_model(),
        collection_name=QDRANT_COLLECTION_NAME,
        client=client
    )

    return {"status": "success", "message": "Document stored successfully"}

def get_retriver():
    client = QdrantClient(host=QDRANT_URL, api_key=QDRANT_API_KEY)
    vector_db = QdrantVectorStore(
        collection_name=QDRANT_COLLECTION_NAME,
        client=client,
        embedding=get_embedding_model()
    )
    if not client.collection_exists(QDRANT_COLLECTION_NAME):
        raise ValueError("No documents uploaded yet. Please upload a PDF first.")
    
    retriever = vector_db.as_retriever(search_type="similarity", search_kwargs={"k": 4})
    return retriever
