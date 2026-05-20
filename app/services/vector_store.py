from app.models.domain import StoredChunk


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


vector_store = InMemoryVectorStore()
