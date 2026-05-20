from dataclasses import dataclass


@dataclass(frozen=True)
class StoredChunk:
    document_id: str
    chunk_id: str
    content: str
    embedding: list[float]
    title: str | None = None


@dataclass(frozen=True)
class RetrievedChunk:
    document_id: str
    chunk_id: str
    content: str
    score: float
    title: str | None = None


@dataclass(frozen=True)
class StoredDocument:
    document_id: str
    title: str | None
    chunks_created: int
