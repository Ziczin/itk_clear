from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.inbox_repo import IInboxRepo
from src.domain.inbox import InboxEntry
from src.infrastructure.models.inbox import InboxDB
from src.utils.logger import logger


class InboxRepo(IInboxRepo):
    """SQLAlchemy implementation for idempotency tracking operations."""

    def __init__(self) -> None:
        self.session: AsyncSession | None = None

    async def add(self, entry: InboxEntry) -> None:
        """Store a processed event key to prevent duplicate handling."""
        if self.session is None:
            raise RuntimeError("Session not initialized")

        logger.info(
            "INBOX REPO | Adding entry to inbox",
            entry_id=entry.id,
            idempotency_key=entry.idempotency_key,
        )
        db_entry = InboxDB(id=entry.id, idempotency_key=str(entry.idempotency_key))
        self.session.add(db_entry)

    async def exists(self, idempotency_key: str) -> bool:
        """Check whether an event key has already been processed."""
        if self.session is None:
            raise RuntimeError("Session not initialized")

        logger.info(
            "INBOX REPO | Check is entry Exists by idempotency key",
            idempotency_key=idempotency_key,
        )
        result = await self.session.execute(
            select(InboxDB).where(InboxDB.idempotency_key == idempotency_key)
        )
        exists = result.scalar_one_or_none() is not None
        logger.info(f"INBOX REPO | Entry {'exist' if exists else 'NOT exist'}")
        return exists

    async def get_by_idempotency_key(self, key: str) -> InboxEntry | None:
        """Retrieve an inbox entry by its idempotency key."""
        if self.session is None:
            raise RuntimeError("Session not initialized")

        result = await self.session.execute(
            select(InboxDB).where(InboxDB.idempotency_key == key)
        )
        db_entry = result.scalar_one_or_none()
        if db_entry:
            return InboxEntry(
                id=db_entry.id,  # type: ignore[arg-type]
                idempotency_key=db_entry.idempotency_key,  # type: ignore[arg-type]
            )
        return None
