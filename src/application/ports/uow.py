from abc import ABC, abstractmethod
from src.application.ports.order_repo import IOrderRepo
from src.application.ports.outbox_repo import IOutboxRepo
from src.application.ports.inbox_repo import IInboxRepo


class IUoW(ABC):
    """Interface for transactional unit of work management."""

    class CommitError(Exception):
        """Database transaction commit failed."""

    class RollbackError(Exception):
        """Database transaction rollback failed."""

    @property
    @abstractmethod
    def orders(self) -> IOrderRepo:
        pass

    @property
    @abstractmethod
    def outbox(self) -> IOutboxRepo:
        pass

    @property
    @abstractmethod
    def inbox(self) -> IInboxRepo:
        pass

    @abstractmethod
    async def commit(self):
        pass

    @abstractmethod
    async def rollback(self):
        pass
