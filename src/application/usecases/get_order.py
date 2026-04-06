from src.application.ports.uow import IUoW
from src.application.ports.order_repo import OrderNotFoundError
from src.utils.context_vars import logger
from uuid import UUID


class GetOrderUseCase:
    """Application service for retrieving order details."""

    def __init__(self, uow: IUoW):
        """Inject transactional unit dependency."""
        self.uow = uow

    async def execute(self, order_id: UUID):
        """Fetch and return a domain order entity by identifier."""
        logger.info("Fetching order details", order_id=str(order_id))

        async with self.uow as uow:
            order = await uow.orders.get(order_id=order_id)
            if order is None:
                raise OrderNotFoundError()

            logger.info("Order retrieved successfully", status=order.status)
            return order
