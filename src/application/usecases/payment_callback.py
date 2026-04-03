from src.domain.outbox import OutboxEntry
from src.application.ports.uow import IUoW
from src.application.ports.order_repo import OrderNotFoundError
from src.utils.logger import logger
from uuid import UUID
import asyncio


class PaymentCallbackUseCase:
    """Application service handling external payment gateway responses."""

    def __init__(self, uow: IUoW, notification_client):
        """Inject transactional unit and notification dependencies."""
        self.uow = uow
        self.notification_client = notification_client

    async def execute(
        self,
        order_id: UUID,
        payment_status: str,
        payment_id: UUID,
        idempotency_key: UUID,
    ):
        """Process payment result and transition order state accordingly."""
        async with logger("UC.PaymentCallback.execute"):
            logger.info(
                "Processing payment result",
                order_id=str(order_id),
                payment_status=payment_status,
            )

            async with self.uow as uow:
                order = await uow.orders.get(order_id=order_id)
                if order is None:
                    raise OrderNotFoundError()

                if payment_status == "succeeded":
                    order.transition_to_paid()

                    event = OutboxEntry(
                        event_type="order.paid",
                        payload={
                            "order_id": str(order.id),
                            "item_id": str(order.item_id),
                            "quantity": order.quantity,
                        },
                        idempotency_key=idempotency_key,
                    )
                    await uow.outbox.add(entry=event)

                    logger.info(
                        "Order marked paid and outbox record created",
                        order_id=str(order.id),
                    )
                    asyncio.create_task(
                        self.notification_client.send(
                            message="Ваш заказ успешно оплачен",
                            reference_id=str(order.id),
                            idempotency_key=str(idempotency_key),
                        )
                    )
                else:
                    order.transition_to_cancelled()
                    logger.warning(
                        "Order cancelled due to payment failure", order_id=str(order.id)
                    )

                await uow.commit()
                logger.info("Callback processing completed", order_id=str(order_id))
