from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.order import Order
from src.utils.exceptions import BaseAppError


class OrderNotFoundError(BaseAppError):
    """Raised when a target order entity cannot be located."""

    default_message = "Order entity not found"


class OrderDuplicateError(BaseAppError):
    """Raised when an idempotency key collision is detected."""

    default_message = "Idempotency key already used"


class IOrderRepo(ABC):
    """Abstract interface for order persistence operations."""

    @abstractmethod
    async def add(self, order: Order) -> None:
        """Stage an order for insertion."""
        ...

    @abstractmethod
    async def get(self, order_id: UUID) -> Order | None:
        """Retrieve an order by its ID."""
        ...

    @abstractmethod
    async def get_by_idempotency_key(self, key: str) -> Order | None:
        """Retrieve an order by its idempotency key."""
        ...

    @abstractmethod
    async def update(self, order: Order) -> None:
        """Update an existing order."""
        ...
