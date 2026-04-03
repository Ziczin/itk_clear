from abc import ABC, abstractmethod
from uuid import UUID

from src.utils.exceptions import BaseAppError


class OrderNotFoundError(BaseAppError):
    """Raised when a target order entity cannot be located."""

    default_message = "Order entity not found"


class OrderDuplicateError(BaseAppError):
    """Raised when an idempotency key collision is detected."""

    default_message = "Idempotency key already used"


class IOrderRepo(ABC):
    """Abstract interface defining order persistence operations."""

    @abstractmethod
    async def add(self, order, idempotency_key: UUID):
        """Insert a new order entity into the data store."""
        pass

    @abstractmethod
    async def get(self, order_id: UUID):
        """Retrieve an order entity by its primary key identifier."""
        pass

    @abstractmethod
    async def update(self, order):
        """Apply state changes to an existing order record."""
        pass

    @abstractmethod
    async def get_by_idempotency_key(self, idempotency_key: UUID):
        """Locate an order using its idempotency constraint key."""
        pass
