from fastapi import APIRouter

from app.models.responses import DocumentResponse
from app.services.vector_store import vector_store

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[DocumentResponse])
def list_documents() -> list[DocumentResponse]:
    return [
        DocumentResponse(
            document_id=document.document_id,
            title=document.title,
            chunks_created=document.chunks_created,
        )
        for document in vector_store.list_documents()
    ]
