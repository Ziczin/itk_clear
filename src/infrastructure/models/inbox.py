from sqlalchemy import Column, String
from src.infrastructure.database import Base


class InboxDB(Base):
    """Database table mapping for processed event idempotency tracking."""

    __tablename__ = "inbox"
    id = Column(String, primary_key=True)
    idempotency_key = Column(String, unique=True)
