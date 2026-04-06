from src.domain.outbox import OutboxEntry
from src.application.ports.uow import IUoW
from src.application.ports.order_repo import OrderNotFoundError
from src.utils.context_vars import logger
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
        idempotency_key: str,
    ):
        """Process payment result and transition order state accordingly."""
        logger.info(
            "Processing payment result",
            order_id=str(order_id),
            payment_status=payment_status,
            payment_id=str(payment_id),
        )

        async with self.uow as uow:
            order = await uow.orders.get(order_id=order_id)

            if order is None:
                logger.error("Order not found for callback", order_id=str(order_id))
                raise OrderNotFoundError()

            if payment_status == "succeeded":
                order.transition_to_paid()

                event = OutboxEntry(
                    event_type="order.paid",
                    payload={
                        "event_type": "order.paid",
                        "order_id": str(order.id),
                        "item_id": str(order.item_id),
                        "quantity": order.quantity,
                        "idempotency_key": str(idempotency_key),
                    },
                    idempotency_key=idempotency_key,
                )

                await uow.outbox.add(entry=event)

                logger.info(
                    "Order marked paid and outbox record created",
                    order_id=str(order.id),
                )

                asyncio.create_task(
                    self._send_notification_safe(
                        message="Ваш заказ успешно оплачен и готов к отправке",
                        reference_id=str(order.id),
                        idempotency_key=str(idempotency_key),
                    )
                )

            else:
                order.transition_to_cancelled()
                reason = "Payment failed"

                logger.warning(
                    "Order cancelled due to payment failure",
                    order_id=str(order.id),
                    reason=reason,
                )

                asyncio.create_task(
                    self._send_notification_safe(
                        message=f"Ваш заказ отменен. Причина: {reason}",
                        reference_id=str(order.id),
                        idempotency_key=str(idempotency_key),
                    )
                )

            await uow.orders.update(order)
            await uow.commit()

            logger.info(
                "Callback processing completed",
                order_id=str(order_id),
                new_status=order.status,
            )

    async def _send_notification_safe(
        self, message: str, reference_id: str, idempotency_key: str
    ):
        """Send notification without blocking the main flow."""
        try:
            await self.notification_client.send(
                message=message,
                reference_id=reference_id,
                idempotency_key=idempotency_key,
            )
        except Exception as e:
            logger.error(
                "Failed to send notification (non-blocking)",
                error=str(e),
                reference_id=reference_id,
            )
