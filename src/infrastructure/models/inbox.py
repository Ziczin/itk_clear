from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from src.infrastructure.database import Base


class InboxDB(Base):
    """Database table mapping for processed event idempotency tracking."""

    __tablename__ = "inbox"
    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    idempotency_key = Column(PG_UUID(as_uuid=True), unique=True)
