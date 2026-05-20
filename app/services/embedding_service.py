from openai import OpenAI


def embed_texts(
    texts: list[str],
    *,
    api_key: str,
    model: str,
) -> list[list[float]]:
    if not texts:
        return []

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    client = OpenAI(api_key=api_key)

    try:
        response = client.embeddings.create(
            model=model,
            input=texts,
        )
    except Exception as exc:
        raise RuntimeError("Failed to generate embeddings") from exc

    return [item.embedding for item in response.data]
