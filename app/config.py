from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Document QA API"
    app_version: str = "0.1.0"
    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4.1-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    openai_timeout_seconds: float = 30.0
    openai_max_retries: int = 2
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k: int = 3
    max_file_size_bytes: int = 2_000_000
    max_question_length: int = 1000

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
