from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.config import get_settings
from app.models.responses import IngestResponse
from app.services.chunking_service import chunk_text
from app.services.embedding_service import embed_texts
from app.services.vector_store import vector_store

router = APIRouter(prefix="/ingest", tags=["ingest"])
settings = get_settings()


@router.post("", response_model=IngestResponse, status_code=status.HTTP_200_OK)
async def ingest_document(
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
) -> IngestResponse:
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

    if len(raw_content) > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"uploaded file exceeds the {settings.max_file_size_bytes} byte limit"
            ),
        )

    normalized_title = title.strip() if title and title.strip() else None
    normalized_document_id = str(uuid4())

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

    try:
        embeddings = embed_texts(
            chunks,
            api_key=settings.openai_api_key,
            model=settings.openai_embedding_model,
            timeout_seconds=settings.openai_timeout_seconds,
            max_retries=settings.openai_max_retries,
        )
        vector_store.upsert_document(
            document_id=normalized_document_id,
            title=normalized_title,
            chunks=chunks,
            embeddings=embeddings,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return IngestResponse(
        message="Document ingested successfully",
        document_id=normalized_document_id,
        chunks_created=len(chunks),
    )
