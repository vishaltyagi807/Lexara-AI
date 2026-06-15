from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import AnyUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    APP_NAME: str = "Lexara-AI Gateway"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    SECRET_KEY: str = "change-me-at-least-32-bytes-long-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 1800
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 604800

    COOKIE_DOMAIN: str | None = None
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"
    
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None

    GITHUB_CLIENT_ID: str | None = None
    GITHUB_CLIENT_SECRET: str | None = None

    DISCORD_CLIENT_ID: str | None = None
    DISCORD_CLIENT_SECRET: str | None = None

    MICROSOFT_CLIENT_ID: str | None = None
    MICROSOFT_CLIENT_SECRET: str | None = None

    WEB_OAUTH_REDIRECT_BASE: str = "https://app.lexara.ai"
    MOBILE_OAUTH_REDIRECT_URI: str = "lexara://oauth/callback"
    OAUTH_STATE_TTL_SECONDS: int = 600

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/lexara"

    REDIS_URL: str = "redis://localhost:6379/0"

    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000", "lexara://oauth/callback"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:

        if isinstance(v, str):
            import json

            stripped = v.strip()
            if stripped.startswith("["):
                return json.loads(stripped)
            return [origin.strip() for origin in stripped.split(",")]
        return v

    KAFKA_BOOTSTRAP_SERVERS: str | None = None
    KAFKA_USER_EVENTS_TOPIC: str = "user-events"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings: Settings = get_settings()
