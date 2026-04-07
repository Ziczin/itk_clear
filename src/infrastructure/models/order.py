from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from src.infrastructure.database import Base
from datetime import datetime


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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
