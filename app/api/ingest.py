from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.models.responses import IngestResponse

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post(
    "", response_model=IngestResponse, status_code=status.HTTP_501_NOT_IMPLEMENTED
)
async def ingest_document(
    document_id: str = Form(...),
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
) -> IngestResponse:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="/ingest is not implemented yet",
    )
