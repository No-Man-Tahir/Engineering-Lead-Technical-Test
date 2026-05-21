from math import sqrt

from app.models.domain import RetrievedChunk, StoredChunk, StoredDocument


class InMemoryVectorStore:
    def __init__(self) -> None:
        self._documents: dict[str, list[StoredChunk]] = {}

    def upsert_document(
        self,
        document_id: str,
        title: str | None,
        chunks: list[str],
        embeddings: list[list[float]],
    ) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings must have the same length")

        stored_chunks = [
            StoredChunk(
                document_id=document_id,
                chunk_id=f"{document_id}-{index}",
                content=chunk,
                embedding=embedding,
                title=title,
            )
            for index, (chunk, embedding) in enumerate(zip(chunks, embeddings))
        ]
        self._documents[document_id] = stored_chunks

    def get_document_chunks(self, document_id: str) -> list[StoredChunk]:
        return list(self._documents.get(document_id, []))

    def list_documents(self) -> list[StoredDocument]:
        documents: list[StoredDocument] = []
        for document_id, chunks in self._documents.items():
            title = chunks[0].title if chunks else None
            documents.append(
                StoredDocument(
                    document_id=document_id,
                    title=title,
                    chunks_created=len(chunks),
                )
            )

        return documents

    def search(
        self,
        *,
        document_id: str,
        query_embedding: list[float],
        top_k: int,
    ) -> list[RetrievedChunk]:
        if top_k <= 0:
            return []

        stored_chunks = self._documents.get(document_id, [])
        scored_chunks = [
            RetrievedChunk(
                document_id=chunk.document_id,
                chunk_id=chunk.chunk_id,
                content=chunk.content,
                score=_cosine_similarity(query_embedding, chunk.embedding),
                title=chunk.title,
            )
            for chunk in stored_chunks
        ]
        scored_chunks.sort(key=lambda chunk: chunk.score, reverse=True)
        return scored_chunks[:top_k]


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("embedding dimensions must match")

    left_magnitude = sqrt(sum(value * value for value in left))
    right_magnitude = sqrt(sum(value * value for value in right))
    if left_magnitude == 0 or right_magnitude == 0:
        return 0.0

    dot_product = sum(
        left_value * right_value for left_value, right_value in zip(left, right)
    )
    return dot_product / (left_magnitude * right_magnitude)


vector_store = InMemoryVectorStore()
