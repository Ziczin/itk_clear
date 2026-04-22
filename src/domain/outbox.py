from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4


@dataclass
class OutboxEntry:
    """Reliable storage container for asynchronous event publishing."""

    id: UUID = field(default_factory=uuid4)
    event_type: str = ""
    payload: dict[str, Any] | None = None
    idempotency_key: str | None = None
    status: str = "PENDING"

    def mark_as_published(self) -> None:
        """Update record status to indicate successful Kafka delivery."""
        self.status = "PUBLISHED"
