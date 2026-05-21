from fastapi import APIRouter, HTTPException, status

from app.config import get_settings
from app.models.requests import AskRequest
from app.models.responses import AskResponse
from app.services.llm_service import generate_answer_from_context
from app.services.retrieval_service import retrieve_relevant_chunks
from app.services.vector_store import vector_store

router = APIRouter(prefix="/ask", tags=["ask"])
settings = get_settings()


@router.post("", response_model=AskResponse, status_code=status.HTTP_200_OK)
def ask_question(payload: AskRequest) -> AskResponse:
    document_id = payload.document_id.strip()
    question = payload.question.strip()

    if not document_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="document_id must not be empty",
        )

    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="question must not be empty",
        )

    if len(question) > settings.max_question_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"question exceeds the {settings.max_question_length} character limit"
            ),
        )

    if not vector_store.get_document_chunks(document_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="document_id was not found",
        )

    try:
        retrieved_chunks = retrieve_relevant_chunks(
            document_id=document_id,
            question=question,
            api_key=settings.openai_api_key,
            model=settings.openai_embedding_model,
            top_k=settings.top_k,
            timeout_seconds=settings.openai_timeout_seconds,
            max_retries=settings.openai_max_retries,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    if not retrieved_chunks:
        return AskResponse(
            answer="The document does not provide enough information to answer this question.",
            sources=[],
        )

    try:
        answer = generate_answer_from_context(
            question=question,
            chunks=retrieved_chunks,
            api_key=settings.openai_api_key,
            model=settings.openai_chat_model,
            timeout_seconds=settings.openai_timeout_seconds,
            max_retries=settings.openai_max_retries,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return AskResponse(
        answer=answer,
        sources=[
            {
                "document_id": chunk.document_id,
                "title": chunk.title,
                "chunk_id": chunk.chunk_id,
                "score": chunk.score,
            }
            for chunk in retrieved_chunks
        ],
    )
