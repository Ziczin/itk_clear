from sqlalchemy import Column, String
from src.infrastructure.database import Base
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


class InboxDB(Base):
    """Database table mapping for processed event idempotency tracking."""

    __tablename__ = "inbox"
    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    idempotency_key = Column(String, unique=True)
