from sqlalchemy import Column, String, DateTime, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from src.infrastructure.database import Base
from datetime import datetime


class OrderDB(Base):
    """Database table model for order records."""

    __tablename__ = "orders"
    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    user_id = Column(String)
    item_id = Column(PG_UUID(as_uuid=True))
    quantity = Column(Integer)
    status = Column(String)
    payment_id = Column(PG_UUID(as_uuid=True), nullable=True)
    idempotency_key = Column(PG_UUID(as_uuid=True), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class OutboxDB(Base):
    """Database table model for reliable outbox events."""

    __tablename__ = "outbox"
    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    event_type = Column(String)
    payload = Column(JSON)
    idempotency_key = Column(PG_UUID(as_uuid=True))
    status = Column(String, default="PENDING")


class InboxDB(Base):
    """Database table model for processed event tracking."""

    __tablename__ = "inbox"
    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    idempotency_key = Column(PG_UUID(as_uuid=True), unique=True)
