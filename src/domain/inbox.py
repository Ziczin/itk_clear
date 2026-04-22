from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class InboxEntry:
    """Idempotency tracking record for processing incoming external events."""

    idempotency_key: str
    id: UUID = field(default_factory=uuid4)
