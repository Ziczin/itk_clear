from src.application.ports.uow import IUoW
from src.application.ports.order_repo import IOrderRepo
from src.utils.logger import logger
from uuid import UUID


class GetOrderUC:
    """Use case for retrieving order details by identifier."""

    def __init__(self, uow: IUoW):
        """Initialize unit of work dependency."""
        self.uow = uow

    async def execute(self, oid: UUID):
        """Fetch order entity and return domain object."""

        async with logger("UC.GetOrder.execute"):
            logger.info("Fetching order details", order_id=str(oid))

            async with self.uow as uow:
                order = await uow.orders.get(oid)
                
                if not order:
                    raise IOrderRepo.NotFound("Order not found")
                
                logger.info("Order retrieved successfully", status=order.status.value)
                return order
