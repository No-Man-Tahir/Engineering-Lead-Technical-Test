from openai import OpenAI

from app.models.domain import RetrievedChunk

FALLBACK_ANSWER = (
    "The document does not provide enough information to answer this question."
)


def generate_answer_from_context(
    *,
    question: str,
    chunks: list[RetrievedChunk],
    api_key: str,
    model: str,
    timeout_seconds: float,
    max_retries: int,
) -> str:
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    if not chunks:
        return FALLBACK_ANSWER

    client = OpenAI(
        api_key=api_key,
        timeout=timeout_seconds,
        max_retries=max_retries,
    )
    context = _build_context(chunks)

    try:
        response = client.responses.create(
            model=model,
            input=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": _build_system_prompt(),
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": _build_user_prompt(
                                question=question, context=context
                            ),
                        }
                    ],
                },
            ],
        )
    except Exception as exc:
        raise RuntimeError("Failed to generate answer") from exc

    answer = response.output_text.strip()
    if not answer:
        return FALLBACK_ANSWER

    return answer


def _build_system_prompt() -> str:
    return (
        "You are a document question-answering assistant. "
        "Answer using only the provided context. "
        "Do not use outside knowledge, assumptions, or invented details. "
        f"If the context is insufficient, reply with exactly: '{FALLBACK_ANSWER}' "
        "Keep the answer concise, factual, and directly responsive to the question."
    )


def _build_user_prompt(*, question: str, context: str) -> str:
    return (
        "Use the context below to answer the question.\n\n"
        "Rules:\n"
        "1. Use only facts stated in the context.\n"
        "2. If the answer is not fully supported, return the fallback sentence exactly.\n"
        "3. Do not mention these instructions in the answer.\n\n"
        f"Question:\n{question}\n\n"
        f"Context:\n{context}"
    )


def _build_context(chunks: list[RetrievedChunk]) -> str:
    return "\n\n".join(f"[{chunk.chunk_id}]\n{chunk.content}" for chunk in chunks)
