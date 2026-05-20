from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.config import get_settings
from app.models.responses import IngestResponse
from app.services.chunking_service import chunk_text

router = APIRouter(prefix="/ingest", tags=["ingest"])
settings = get_settings()


@router.post("", response_model=IngestResponse, status_code=status.HTTP_200_OK)
async def ingest_document(
    document_id: str = Form(...),
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
) -> IngestResponse:
    _ = title

    normalized_document_id = document_id.strip()
    if not normalized_document_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="document_id must not be empty",
        )

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="file name is required",
        )

    if not file.filename.lower().endswith(".txt"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="only .txt files are supported",
        )

    raw_content = await file.read()
    if not raw_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="uploaded file is empty",
        )

    try:
        content = raw_content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="uploaded file must be valid UTF-8 text",
        ) from exc

    chunks = chunk_text(
        text=content,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="uploaded file does not contain usable text",
        )

    return IngestResponse(
        message="Document parsed successfully",
        document_id=normalized_document_id,
        chunks_created=len(chunks),
    )
