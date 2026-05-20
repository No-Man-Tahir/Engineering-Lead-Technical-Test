from fastapi import FastAPI

from app.api.ask import router as ask_router
from app.api.documents import router as documents_router
from app.api.ingest import router as ingest_router
from app.config import get_settings
from app.models.responses import HealthResponse
from app.ui import router as ui_router

settings = get_settings()

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.include_router(ui_router)
app.include_router(ingest_router)
app.include_router(documents_router)
app.include_router(ask_router)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok", app_name=settings.app_name, version=settings.app_version
    )
