from abc import ABC, abstractmethod

from src.domain.inbox import InboxEntry


class IInboxRepo(ABC):
    @abstractmethod
    async def add(self, entry: InboxEntry) -> None: ...

    @abstractmethod
    async def exists(self, idempotency_key: str) -> bool: ...

    @abstractmethod
    async def get_by_idempotency_key(self, key: str) -> InboxEntry | None: ...
