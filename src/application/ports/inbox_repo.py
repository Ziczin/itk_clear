from abc import ABC, abstractmethod
from uuid import UUID


class IInboxRepo(ABC):
    """Interface for processed events idempotency tracking."""

    class CheckError(Exception):
        """Failed to verify processing status."""

    @abstractmethod
    async def add(self, entry):
        pass

    @abstractmethod
    async def exists(self, key: UUID) -> bool:
        pass
