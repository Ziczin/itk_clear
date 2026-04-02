from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import HttpUrl


class Config(BaseSettings):
    """Global application settings container."""

    DATABASE_URL: str
    KAFKA_BOOTSTRAP_SERVERS: str
    CAPASHINO_API_KEY: str
    CATALOG_URL: HttpUrl
    PAYMENTS_URL: HttpUrl
    NOTIFICATIONS_URL: HttpUrl
    PAYMENT_CALLBACK_URL: HttpUrl
    APP_ENV: str = "development"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Config()
