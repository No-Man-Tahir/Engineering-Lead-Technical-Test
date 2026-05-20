from app.models.domain import RetrievedChunk
from app.services.embedding_service import embed_texts
from app.services.vector_store import vector_store


def retrieve_relevant_chunks(
    *,
    document_id: str,
    question: str,
    api_key: str,
    model: str,
    top_k: int,
) -> list[RetrievedChunk]:
    question_embedding = embed_texts([question], api_key=api_key, model=model)[0]
    return vector_store.search(
        document_id=document_id,
        query_embedding=question_embedding,
        top_k=top_k,
    )
