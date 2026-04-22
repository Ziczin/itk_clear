from typing import Optional

from pydantic import HttpUrl
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

    _CATALOG_URL: HttpUrl
    _PAYMENTS_URL: HttpUrl
    _NOTIFICATIONS_URL: HttpUrl
    _PAYMENTS_CALLBACK_URL: HttpUrl

    PAYMENTS_RETRY_LIMIT: int = 5
    PAYMENTS_START_TIMEOUT: float = 1.0
    PAYMENTS_MAX_TIMEOUT: float = 10.0

    SENTRY_DSN: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

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
