from types import TracebackType
from typing import Type  # Нужно только для Type[BaseException] в __aexit__

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.uow import IUoW
from src.infrastructure.database import async_session_maker
from src.infrastructure.repos.inbox import InboxRepo
from src.infrastructure.repos.order import OrderRepo
from src.infrastructure.repos.outbox import OutboxRepo
from src.utils.logger import logger


class UoW(IUoW):
    """Concrete implementation managing transactional session lifecycle."""

    def __init__(self) -> None:
        self.session: AsyncSession | None = None

        self._orders = OrderRepo()
        self._outbox = OutboxRepo()
        self._inbox = InboxRepo()

    async def __aenter__(self) -> "UoW":
        """Open database session and bind repositories to it."""
        self.session = async_session_maker()

        self._orders.session = self.session
        self._outbox.session = self.session
        self._inbox.session = self.session

        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Close database session upon context exit."""
        if self.session is None:
            return

        try:
            if exc_type is not None:
                await self.session.rollback()
                logger.warning(
                    "UNIT OF WORK | UoW transaction rolled back due to exception"
                )
            else:
                await self.session.commit()
        finally:
            await self.session.close()

    async def commit(self) -> None:
        """Persist all staged changes to the database."""
        if self.session is None:
            raise RuntimeError("Session is not initialized. Did you use 'async with'?")
        await self.session.commit()

    async def rollback(self) -> None:
        """Revert all staged changes in the current session."""
        if self.session is None:
            raise RuntimeError("Session is not initialized. Did you use 'async with'?")
        await self.session.rollback()
        logger.warning("UNIT OF WORK | UoW transaction rolled back")

    @property
    def orders(self) -> OrderRepo:
        return self._orders

    @property
    def outbox(self) -> OutboxRepo:
        return self._outbox

    @property
    def inbox(self) -> InboxRepo:
        return self._inbox
