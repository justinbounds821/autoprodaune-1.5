from __future__ import annotations

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    This minimal settings object is sufficient for tests and can be extended
    as the application evolves. Environment variables take precedence.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )

    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=False)

    SECRET_KEY: str = Field(default="change-me")

    SUPABASE_URL: str = Field(default="")
    SUPABASE_KEY: str = Field(default="")

    REDIS_URL: str = Field(default="redis://localhost:6379/0")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance, populated from env/.env."""
    return Settings()
