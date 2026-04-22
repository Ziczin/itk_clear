from typing import Any, Optional

from pydantic import HttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Global settings container loaded from environment variables."""

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DATABASE_NAME: str
    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str

    DATABASE_URL: str

    KAFKA_BOOTSTRAP_SERVERS: str

    CAPASHINO_API_KEY: str

    _CATALOG_URL: HttpUrl
    _PAYMENTS_URL: HttpUrl
    _NOTIFICATIONS_URL: HttpUrl
    _PAYMENTS_CALLBACK_URL: HttpUrl

    PAYMENTS_RETRY_LIMIT: int = 5
    PAYMENTS_START_TIMEOUT: float = 1.0
    PAYMENTS_MAX_TIMEOUT: float = 10.0

    SENTRY_DSN: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def build_database_url(cls, v: str | None, info: Any) -> str:
        """Build DATABASE_URL from individual PostgreSQL parameters if not provided."""
        if v:
            return v
        data = info.data
        return (
            f"postgresql+asyncpg://"
            f"{data['POSTGRES_USERNAME']}:{data['POSTGRES_PASSWORD']}@"
            f"{data['POSTGRES_HOST']}:{data['POSTGRES_PORT']}/"
            f"{data['POSTGRES_DATABASE_NAME']}"
        )

    @property
    def CATALOG_URL(self) -> str:
        return str(self._CATALOG_URL).rstrip("/")

    @property
    def PAYMENTS_URL(self) -> str:
        return str(self._PAYMENTS_URL).rstrip("/")

    @property
    def NOTIFICATIONS_URL(self) -> str:
        return str(self._NOTIFICATIONS_URL).rstrip("/")

    @property
    def PAYMENTS_CALLBACK_URL(self) -> str:
        return str(self._PAYMENTS_CALLBACK_URL).rstrip("/")

    @property
    def DATABASE_URL_SYNC(self) -> str:
        """Return sync version of DATABASE_URL for Alembic CLI."""
        url = self.DATABASE_URL
        if url and "postgresql+asyncpg://" in url:
            return url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
        return (
            f"postgresql+psycopg2://"
            f"{self.POSTGRES_USERNAME}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DATABASE_NAME}"
        )


settings = Config()  # type: ignore[reportCallIssue]
