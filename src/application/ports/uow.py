from abc import ABC, abstractmethod

from src.application.ports.inbox_repo import IInboxRepo
from src.application.ports.order_repo import IOrderRepo
from src.application.ports.outbox_repo import IOutboxRepo
from src.utils.exceptions import BaseAppError


class UoWCommitError(BaseAppError):
    """Raised when a database transaction commit fails."""

    default_message = "Transaction commit failed"


class UoWRollbackError(BaseAppError):
    """Raised when a database transaction rollback fails."""

    default_message = "Transaction rollback failed"


class IUoW(ABC):
    """Abstract interface managing transactional unit boundaries."""

    @property
    @abstractmethod
    def orders(self) -> IOrderRepo:
        """Provide access to the order repository instance."""
        pass

    @property
    @abstractmethod
    def outbox(self) -> IOutboxRepo:
        """Provide access to the outbox repository instance."""
        pass

    @property
    @abstractmethod
    def inbox(self) -> IInboxRepo:
        """Provide access to the inbox repository instance."""
        pass

    @abstractmethod
    async def commit(self):
        """Persist all staged transactional changes to the database."""
        pass

    @abstractmethod
    async def rollback(self):
        """Revert all staged transactional changes in the current session."""
        pass

    @abstractmethod
    async def __aenter__(self):
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
