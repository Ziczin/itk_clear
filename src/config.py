from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import HttpUrl
from typing import Optional


class Config(BaseSettings):
    """Global settings container loaded from environment variables."""

    DATABASE_URL: str
    KAFKA_BOOTSTRAP_SERVERS: str
    CAPASHINO_API_KEY: str
    CATALOG_URL: HttpUrl
    PAYMENTS_URL: HttpUrl
    NOTIFICATIONS_URL: HttpUrl
    PAYMENT_CALLBACK_URL: HttpUrl
    SENTRY_DSN: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Config()
