from uuid import UUID

from sqlalchemy import select
from sqlalchemy import update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.outbox_repo import IOutboxRepo
from src.domain.outbox import OutboxEntry
from src.infrastructure.models.outbox import OutboxDB
from src.utils.logger import logger


class OutboxRepo(IOutboxRepo):
    """SQLAlchemy implementation for outbox event persistence operations."""

    def __init__(self) -> None:
        self.session: AsyncSession | None = None

    async def add(self, entry: OutboxEntry) -> None:
        """Queue a new event entry for asynchronous publishing."""
        if self.session is None:
            raise RuntimeError("Session not initialized")

        logger.info(
            "OUTBOX REPO | Adding entry to outbox",
            id=entry.id,
            event_type=entry.event_type,
            payload=entry.payload,
            idempotency_key=entry.idempotency_key,
        )
        db_entry = OutboxDB(
            id=entry.id,
            event_type=entry.event_type,
            payload=entry.payload,
            idempotency_key=entry.idempotency_key,
            status=entry.status,
        )
        self.session.add(db_entry)

    async def get_pending(self, limit: int = 10) -> list[OutboxEntry]:
        """Retrieve a limited batch of unpublished event entries."""
        if self.session is None:
            raise RuntimeError("Session not initialized")

        result = await self.session.execute(
            select(OutboxDB).where(OutboxDB.status == "PENDING").limit(limit)
        )
        db_entries = result.scalars().all()
        return [
            OutboxEntry(
                id=e.id,  # type: ignore[arg-type]
                event_type=e.event_type,  # type: ignore[arg-type]
                payload=e.payload,  # type: ignore[arg-type]
                idempotency_key=e.idempotency_key,  # type: ignore[arg-type]
                status=e.status,  # type: ignore[arg-type]
            )
            for e in db_entries
        ]

    async def mark_as_published(self, entry_id: UUID) -> None:
        """Update an event entry status to indicate successful delivery."""
        if self.session is None:
            raise RuntimeError("Session not initialized")

        logger.info("OUTBOX REPO | event marked published", entry_id=entry_id)
        await self.session.execute(
            sa_update(OutboxDB)
            .where(OutboxDB.id == entry_id)
            .values(status="PUBLISHED")
        )
