from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.infrastructure.database import Base


def utc_datettime() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class OrderDB(Base):
    """Database table mapping for persistent order records."""

    __tablename__ = "orders"
    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    user_id = Column(String)
    item_id = Column(PG_UUID(as_uuid=True))
    quantity = Column(Integer)
    status = Column(String)
    payment_id = Column(PG_UUID(as_uuid=True), nullable=True)
    idempotency_key = Column(String, unique=True)
    created_at = Column(DateTime, default=utc_datettime)
    updated_at = Column(DateTime, default=utc_datettime)
