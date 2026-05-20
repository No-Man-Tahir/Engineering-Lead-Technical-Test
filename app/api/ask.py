from fastapi import APIRouter, HTTPException, status

from app.models.requests import AskRequest
from app.models.responses import AskResponse

router = APIRouter(prefix="/ask", tags=["ask"])


@router.post(
    "", response_model=AskResponse, status_code=status.HTTP_501_NOT_IMPLEMENTED
)
def ask_question(payload: AskRequest) -> AskResponse:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="/ask is not implemented yet",
    )
