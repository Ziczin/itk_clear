from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self

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
        ...

    @property
    @abstractmethod
    def outbox(self) -> IOutboxRepo:
        """Provide access to the outbox repository instance."""
        ...

    @property
    @abstractmethod
    def inbox(self) -> IInboxRepo:
        """Provide access to the inbox repository instance."""
        ...

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...

    @abstractmethod
    async def __aenter__(self) -> Self: ...

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...
