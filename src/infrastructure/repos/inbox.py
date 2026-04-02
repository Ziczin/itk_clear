from sqlalchemy import select
from src.application.ports.inbox_repo import IInboxRepo
from src.infrastructure.orm_models import InboxDB
from uuid import UUID


class InboxRepo(IInboxRepo):
    """SQLAlchemy implementation for idempotency tracking."""

    def __init__(self):
        self.session = None

    async def add(self, entry):
        """Record processed event key for future deduplication."""
        db_entry = InboxDB(id=entry.id, idempotency_key=entry.idempotency_key)
        self.session.add(db_entry)

    async def exists(self, key: UUID) -> bool:
        """Check if event key already processed."""
        res = await self.session.execute(
            select(InboxDB).where(InboxDB.idempotency_key == key)
        )
        return res.scalar_one_or_none() is not None
