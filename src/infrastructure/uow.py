from src.application.ports.uow import IUoW
from src.infrastructure.database import async_session_maker
from src.infrastructure.repos.order import OrderRepo
from src.infrastructure.repos.outbox import OutboxRepo
from src.infrastructure.repos.inbox import InboxRepo
from src.utils.context_vars import logger


class UoW(IUoW):
    """Concrete implementation managing transactional session lifecycle."""

    def __init__(self):
        self.session = None
        self._orders = OrderRepo()
        self._outbox = OutboxRepo()
        self._inbox = InboxRepo()

    async def __aenter__(self):
        """Open database session and bind repositories to it."""
        self.session = async_session_maker()
        self._orders.session = self.session
        self._outbox.session = self.session
        self._inbox.session = self.session
        logger.debug("UoW session opened")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close database session upon context exit."""
        await self.session.close()
        logger.debug("UoW session closed")

    async def commit(self):
        """Persist all staged changes to the database."""
        await self.session.commit()
        logger.info("UoW transaction committed")

    async def rollback(self):
        """Revert all staged changes in the current session."""
        await self.session.rollback()
        logger.warning("UoW transaction rolled back")

    @property
    def orders(self):
        """Expose the order repository instance."""
        return self._orders

    @property
    def outbox(self):
        """Expose the outbox repository instance."""
        return self._outbox

    @property
    def inbox(self):
        """Expose the inbox repository instance."""
        return self._inbox
