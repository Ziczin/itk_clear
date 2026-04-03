from uuid import UUID, uuid4
from dataclasses import dataclass, field


@dataclass
class InboxEntry:
    """Idempotency tracking record for processing incoming external events."""

    id: UUID = field(default_factory=uuid4)
    idempotency_key: UUID = None
