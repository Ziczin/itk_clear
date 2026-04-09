from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import HttpUrl, field_validator
from typing import Optional


class Config(BaseSettings):
    """Global settings container loaded from environment variables."""

    # Application settings
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_RELOAD: bool = False
    APP_LOG_LEVEL: str = "INFO"

    # Database settings
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DATABASE_NAME: str
    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str

    DATABASE_URL: Optional[str] = None

    # Kafka settings
    KAFKA_BOOTSTRAP_SERVERS: str

    # External API settings
    CAPASHINO_API_KEY: str

    CATALOG_URL: HttpUrl

    PAYMENTS_URL: HttpUrl
    PAYMENTS_RETRY_LIMIT: int = 5
    PAYMENTS_START_TIMEOUT: float = 1.0
    PAYMENTS_MAX_TIMEOUT: float = 10.0
    PAYMENTS_CALLBACK_URL: HttpUrl

    NOTIFICATIONS_URL: HttpUrl

    # Monitoring settings
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

    def model_post_init(self, __context):
        # Приводим HttpUrl к строке и обрезаем завершающий слэш, если он есть
        self.CATALOG_URL = str(self.CATALOG_URL).rstrip("/")
        self.PAYMENTS_URL = str(self.PAYMENTS_URL).rstrip("/")
        self.NOTIFICATIONS_URL = str(self.NOTIFICATIONS_URL).rstrip("/")
        self.PAYMENTS_CALLBACK_URL = str(self.PAYMENTS_CALLBACK_URL).rstrip("/")

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


settings = Config()
