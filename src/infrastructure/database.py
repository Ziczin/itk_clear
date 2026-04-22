from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import settings

engine = create_async_engine(settings.DATABASE_URL_STRING, echo=False)
"""Create asynchronous database engine using configured connection string."""

async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
"""Factory function producing new asynchronous database sessions."""


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy ORM models."""

    ...
