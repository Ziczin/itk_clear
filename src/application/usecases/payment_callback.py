from src.domain.models import OutboxEntry
from src.application.ports.uow import IUoW
from src.application.ports.order_repo import IOrderRepo
from src.utils.logger import logger
from uuid import UUID
import asyncio


class PaymentCallbackUC:
    """Use case for handling external payment gateway results."""

    def __init__(self, uow: IUoW, notify):
        """Initialize dependencies for payment result processing."""
        self.uow = uow
        self.notify = notify

    async def execute(self, oid: UUID, status: str, pid: UUID, key: UUID):
        """Process payment callback and transition order state."""

        async with logger("UC.PaymentCallback.execute"):
            logger.info("Processing payment result", order_id=str(oid), status=status)

            async with self.uow as uow:
                order = await uow.orders.get(oid)

                if not order:
                    raise IOrderRepo.NotFound("Order not found for callback")
                
                if status == "succeeded":
                    order.mark_paid()
                    event = OutboxEntry(
                        event_type="order.paid",
                        payload={
                            "order_id": str(order.id),
                            "item_id": str(order.item_id),
                            "quantity": order.quantity,
                        },
                        idempotency_key=key,
                    )

                    await uow.outbox.add(event)

                    logger.info(
                        "Order marked paid and outbox record created",
                        order_id=str(order.id),
                    )

                    asyncio.create_task(
                        self.notify.send(
                            "Ваш заказ успешно оплачен", str(order.id), str(key)
                        )
                    )

                else:
                    order.mark_cancelled()
                    logger.warning(
                        "Order cancelled due to payment failure", order_id=str(order.id)
                    )
                    
                await uow.commit()
                logger.info("Callback processing completed", order_id=str(order.id))
