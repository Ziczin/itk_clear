from sqlalchemy import Column, String, JSON
from src.infrastructure.database import Base


class OutboxDB(Base):
    """Database table mapping for reliable outbox event storage."""

    __tablename__ = "outbox"
    id = Column(String, primary_key=True)
    event_type = Column(String)
    payload = Column(JSON)
    idempotency_key = Column(String)
    status = Column(String, default="PENDING")
