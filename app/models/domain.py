from dataclasses import dataclass


@dataclass(frozen=True)
class StoredChunk:
    document_id: str
    chunk_id: str
    content: str
    embedding: list[float]
    title: str | None = None
