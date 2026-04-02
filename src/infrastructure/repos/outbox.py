from sqlalchemy import select, update
from src.application.ports.outbox_repo import IOutboxRepo
from src.infrastructure.orm_models import OutboxDB
from uuid import UUID


class OutboxRepo(IOutboxRepo):
    """SQLAlchemy implementation for outbox event persistence."""

    def __init__(self):
        self.session = None

    async def add(self, entry):
        """Queue new event for asynchronous publishing."""
        db_entry = OutboxDB(
            id=entry.id,
            event_type=entry.event_type,
            payload=entry.payload,
            idempotency_key=entry.idempotency_key,
        )
        self.session.add(db_entry)

    async def get_pending(self, limit=10):
        """Retrieve limited batch of unpublished events."""
        res = await self.session.execute(
            select(OutboxDB).where(OutboxDB.status == "PENDING").limit(limit)
        )
        return res.scalars().all()

    async def mark_published(self, eid: UUID):
        """Update event status to successfully published."""
        await self.session.execute(
            update(OutboxDB).where(OutboxDB.id == eid).values(status="PUBLISHED")
        )
