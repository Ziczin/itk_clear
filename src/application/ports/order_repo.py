from abc import ABC, abstractmethod
from uuid import UUID


class IOrderRepo(ABC):
    """Interface for order persistence operations."""

    class NotFound(Exception):
        """Target order does not exist."""

    class Duplicate(Exception):
        """Idempotency key collision detected."""

    @abstractmethod
    async def add(self, order, key: UUID):
        pass

    @abstractmethod
    async def get(self, oid: UUID) -> object:
        pass

    @abstractmethod
    async def update(self, order):
        pass

    @abstractmethod
    async def get_by_key(self, key: UUID) -> object:
        pass
