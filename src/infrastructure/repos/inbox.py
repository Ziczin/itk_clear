from sqlalchemy import select

from src.application.ports.inbox_repo import IInboxRepo
from src.infrastructure.models.inbox import InboxDB
from src.utils.logger import logger


class InboxRepo(IInboxRepo):
    """SQLAlchemy implementation for idempotency tracking operations."""

    def __init__(self):
        self.session = None

    async def add(self, entry):
        """Store a processed event key to prevent duplicate handling."""
        logger.info(
            "INBOX REPO | Adding entry to inbox",
            entry_id=entry.id,
            idempotency_key=entry.idempotency_key,
        )
        db_entry = InboxDB(id=entry.id, idempotency_key=str(entry.idempotency_key))
        self.session.add(db_entry)

    async def exists(self, idempotency_key: str) -> bool:
        """Check whether an event key has already been processed."""
        logger.info(
            "INBOX REPO | Check is entry exists by idempotency key",
            idempotency_key=idempotency_key,
        )
        result = await self.session.execute(
            select(InboxDB).where(InboxDB.idempotency_key == idempotency_key)
        )
        logger.info(
            f"INBOX REPO | Entry {'exist' if result.scalar_one_or_none() is not None else 'NOT exist'}"
        )
        return result.scalar_one_or_none() is not None
