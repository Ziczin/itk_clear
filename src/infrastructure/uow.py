from src.application.ports.uow import IUoW
from src.infrastructure.database import async_session_maker
from src.infrastructure.repos.order import OrderRepo
from src.infrastructure.repos.outbox import OutboxRepo
from src.infrastructure.repos.inbox import InboxRepo
from src.utils.logger import logger


class UoW(IUoW):
    """Concrete unit of work managing transactional session lifecycle."""

    def __init__(self):
        self.session = None
        self._orders = OrderRepo()
        self._outbox = OutboxRepo()
        self._inbox = InboxRepo()

    async def __aenter__(self):
        """Open database session and attach to repositories."""
        self.session = async_session_maker()
        self._orders.session = self.session
        self._outbox.session = self.session
        self._inbox.session = self.session
        logger.debug("UoW session opened")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close session on context exit."""
        await self.session.close()
        logger.debug("UoW session closed")

    async def commit(self):
        """Persist all pending changes to database."""
        await self.session.commit()
        logger.info("UoW transaction committed")

    async def rollback(self):
        """Revert all pending changes in session."""
        await self.session.rollback()
        logger.warning("UoW transaction rolled back")

    @property
    def orders(self):
        return self._orders

    @property
    def outbox(self):
        return self._outbox

    @property
    def inbox(self):
        return self._inbox
