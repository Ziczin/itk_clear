from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.outbox import OutboxEntry
from src.utils.exceptions import BaseAppError


class OutboxPersistError(BaseAppError):
    """Raised when saving an outbox entry fails."""

    default_message = "Failed to persist outbox record"


class IOutboxRepo(ABC):
    """Abstract interface for reliable outbox event storage operations."""

    @abstractmethod
    async def add(self, entry: OutboxEntry):
        """Queue a new event entry for asynchronous publishing."""
        ...

    @abstractmethod
    async def get_pending(self, limit: int = 10):
        """Retrieve a limited batch of unpublished event entries."""
        ...

    @abstractmethod
    async def mark_as_published(self, entry_id: UUID):
        """Update an event entry status to indicate successful delivery."""
        ...
