from sqlalchemy import Column, String, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from src.infrastructure.database import Base


class OutboxDB(Base):
    """Database table mapping for reliable outbox event storage."""

    __tablename__ = "outbox"
    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    event_type = Column(String)
    payload = Column(JSON)
    idempotency_key = Column(PG_UUID(as_uuid=True))
    status = Column(String, default="PENDING")
