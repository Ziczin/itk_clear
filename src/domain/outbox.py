from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class OutboxEntry:
    """Reliable storage container for asynchronous event publishing."""

    id: UUID = field(default_factory=uuid4)
    event_type: str = ""
    payload: dict = None
    idempotency_key: str = None
    status: str = "PENDING"

    def mark_as_published(self):
        """Update record status to indicate successful Kafka delivery."""
        self.status = "PUBLISHED"
