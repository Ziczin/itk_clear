from uuid import UUID

from sqlalchemy import select, update

from src.application.ports.outbox_repo import IOutboxRepo
from src.infrastructure.models.outbox import OutboxDB
from src.utils.logger import logger


class OutboxRepo(IOutboxRepo):
    """SQLAlchemy implementation for outbox event persistence operations."""

    def __init__(self):
        self.session = None

    async def add(self, entry):
        """Queue a new event entry for asynchronous publishing."""
        logger.info(
            "Adding entry to outbox",
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
        )
        self.session.add(db_entry)

    async def get_pending(self, limit=10):
        """Retrieve a limited batch of unpublished event entries."""
        result = await self.session.execute(
            select(OutboxDB).where(OutboxDB.status == "PENDING").limit(limit)
        )

        return result.scalars().all()

    async def mark_as_published(self, entry_id: UUID):
        """Update an event entry status to indicate successful delivery."""
        logger.info("OUTBOX REPO | event marked published", entry_id=entry_id)
        await self.session.execute(
            update(OutboxDB).where(OutboxDB.id == entry_id).values(status="PUBLISHED")
        )
