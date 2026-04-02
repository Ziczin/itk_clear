from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from src.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
"""Create async engine with configured database URL."""

async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
"""Factory for async database sessions."""


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy declarative models."""

    pass
