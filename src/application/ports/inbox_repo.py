from abc import ABC, abstractmethod

from src.utils.exceptions import BaseAppError


class InboxCheckError(BaseAppError):
    """Raised when verifying inbox status encounters an error."""

    default_message = "Failed to verify inbox processing status"


class IInboxRepo(ABC):
    """Abstract interface for idempotency tracking of processed events."""

    @abstractmethod
    async def add(self, entry):
        """Store a processed event key to prevent duplicate handling."""
        pass

    @abstractmethod
    async def exists(self, idempotency_key: str) -> bool:
        """Check whether an event key has already been processed."""
        pass
