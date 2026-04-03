from sqlalchemy import select
from src.application.ports.inbox_repo import IInboxRepo
from src.infrastructure.models.inbox import InboxDB
from uuid import UUID


class InboxRepo(IInboxRepo):
    """SQLAlchemy implementation for idempotency tracking operations."""

    def __init__(self):
        self.session = None

    async def add(self, entry):
        """Store a processed event key to prevent duplicate handling."""
        db_entry = InboxDB(id=entry.id, idempotency_key=entry.idempotency_key)
        self.session.add(db_entry)

    async def exists(self, idempotency_key: UUID) -> bool:
        """Check whether an event key has already been processed."""
        result = await self.session.execute(
            select(InboxDB).where(InboxDB.idempotency_key == idempotency_key)
        )
        return result.scalar_one_or_none() is not None
