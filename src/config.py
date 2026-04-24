from typing import Optional

from pydantic import HttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Global settings container loaded from environment variables."""

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DATABASE_NAME: str
    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str

    DATABASE_URL: str | None = None

    KAFKA_BOOTSTRAP_SERVERS: str

    CAPASHINO_API_KEY: str

    CATALOG_URL: str
    PAYMENTS_URL: str
    NOTIFICATIONS_URL: str
    PAYMENTS_CALLBACK_URL: str

    PAYMENTS_RETRY_LIMIT: int = 5
    PAYMENTS_START_TIMEOUT: float = 1.0
    PAYMENTS_MAX_TIMEOUT: float = 10.0

    SENTRY_DSN: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator(
        "CATALOG_URL",
        "PAYMENTS_URL",
        "NOTIFICATIONS_URL",
        "PAYMENTS_CALLBACK_URL",
        mode="before",
    )
    @classmethod
    def validate_and_strip_url(cls, v: str) -> str:
        """Validate URL format and strip trailing slash."""
        HttpUrl(v)
        return v.rstrip("/")

    @property
    def DATABASE_URL_STRING(self) -> str:
        """Guaranteed string version of DATABASE_URL for runtime usage."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USERNAME}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DATABASE_NAME}"
        )

    @property
    def DATABASE_URL_SYNC(self) -> str:
        """Return sync version of DATABASE_URL for Alembic CLI."""
        url = self.DATABASE_URL_STRING
        if "postgresql+asyncpg://" in url:
            return url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
        return (
            f"postgresql+psycopg2://"
            f"{self.POSTGRES_USERNAME}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DATABASE_NAME}"
        )


settings = Config()  # type: ignore[reportCallIssue]
