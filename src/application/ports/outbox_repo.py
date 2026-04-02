from abc import ABC, abstractmethod
from uuid import UUID


class IOutboxRepo(ABC):
    """Interface for reliable outbox event storage."""

    class PersistError(Exception):
        """Failed to persist outbox record."""

    @abstractmethod
    async def add(self, entry):
        pass

    @abstractmethod
    async def get_pending(self, limit: int = 10):
        pass

    @abstractmethod
    async def mark_published(self, eid: UUID):
        pass
