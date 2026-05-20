from fastapi import FastAPI

from app.api.ask import router as ask_router
from app.api.ingest import router as ingest_router
from app.config import get_settings
from app.models.responses import HealthResponse

settings = get_settings()

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.include_router(ingest_router)
app.include_router(ask_router)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok", app_name=settings.app_name, version=settings.app_version
    )
