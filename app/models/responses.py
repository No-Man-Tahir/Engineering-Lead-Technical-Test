from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str


class IngestResponse(BaseModel):
    message: str
    document_id: str
    chunks_created: int


class DocumentResponse(BaseModel):
    document_id: str
    title: str | None
    chunks_created: int


class SourceResponse(BaseModel):
    document_id: str
    chunk_id: str
    score: float


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceResponse]
