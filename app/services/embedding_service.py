from openai import OpenAI


def embed_texts(
    texts: list[str],
    *,
    api_key: str,
    model: str,
    timeout_seconds: float,
    max_retries: int,
) -> list[list[float]]:
    if not texts:
        return []

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    client = OpenAI(
        api_key=api_key,
        timeout=timeout_seconds,
        max_retries=max_retries,
    )

    try:
        response = client.embeddings.create(
            model=model,
            input=texts,
        )
    except Exception as exc:
        raise RuntimeError("Failed to generate embeddings") from exc

    return [item.embedding for item in response.data]
