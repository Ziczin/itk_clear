from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import HttpUrl, field_validator
from typing import Optional


class Config(BaseSettings):
    """Global settings container loaded from environment variables."""

    # Database connection parameters (individual fields)
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DATABASE_NAME: str
    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str

    # Computed DATABASE_URL for SQLAlchemy (asyncpg for app, psycopg2 for alembic)
    DATABASE_URL: Optional[str] = None

    # Other services
    KAFKA_BOOTSTRAP_SERVERS: str
    CAPASHINO_API_KEY: str
    CATALOG_URL: HttpUrl
    PAYMENTS_URL: HttpUrl
    NOTIFICATIONS_URL: HttpUrl
    PAYMENT_CALLBACK_URL: HttpUrl
    SENTRY_DSN: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def build_database_url(cls, v: Optional[str], info) -> str:
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
    def DATABASE_URL_SYNC(self) -> str:
        """Return sync version of DATABASE_URL for Alembic CLI (psycopg2 driver)."""
        return self.DATABASE_URL.replace(
            "postgresql+asyncpg://", "postgresql+psycopg2://"
        )


settings = Config()
