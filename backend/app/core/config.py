from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: Literal["development", "test", "production"] = "development"

    openai_api_key: str

    pinecone_api_key: str
    pinecone_index_name: str = "pdf-ai-assistant"
    pinecone_cloud: str = "aws"
    pinecone_region: str = "us-east-1"

    chat_model: str = "gpt-4.1-mini"
    embedding_model: str = "text-embedding-3-small"

    max_upload_size_mb: int = Field(default=20, ge=1, le=100)
    frontend_origin: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()