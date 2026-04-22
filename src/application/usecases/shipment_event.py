import asyncio
from uuid import UUID, uuid4

from src.application.ports.order_repo import OrderNotFoundError
from src.application.ports.uow import IUoW
from src.domain.inbox import InboxEntry
from src.utils.logger import logger


class ShipmentEventUseCase:
    """Application service for processing shipping service Kafka events."""

    def __init__(self, uow: IUoW, notification_client):
        """Inject transactional unit and notification dependencies."""
        self.uow = uow
        self.notification_client = notification_client

    async def execute(self, event_data: dict):
        """Consume shipment event and update order state idempotently."""
        event_type = event_data.get("event_type")
        order_id = UUID(event_data.get("order_id"))
        idempotency_key = str(event_data.get("idempotency_key", uuid4()))

        logger.info(
            "SHIPMENT USECASE | Processing shipment event",
            event_type=event_type,
            order_id=str(order_id),
            idempotency_key=idempotency_key,
        )

        async with self.uow as uow:
            if await uow.inbox.exists(idempotency_key=idempotency_key):
                logger.warning(
                    "SHIPMENT EVENT | Duplicate event skipped (already processed)",
                    event_key=str(idempotency_key),
                )
                return

            order = await uow.orders.get(order_id=order_id)

            if order is None:
                logger.error(
                    "Order not found for shipment event", order_id=str(order_id)
                )
                raise OrderNotFoundError()

            if event_type == "order.shipped":
                order.transition_to_shipped()
                notification_message = "Ваш заказ отправлен в доставку"

            elif event_type == "order.cancelled":
                order.transition_to_cancelled()
                reason = event_data.get("reason", "unknown")
                notification_message = f"Ваш заказ отменен. Причина: {reason}"

            else:
                logger.warning(
                    "SHIPMENT EVENT | Unknown shipment event type",
                    event_type=event_type,
                )
                return

            await uow.inbox.add(entry=InboxEntry(idempotency_key=idempotency_key))
            await uow.orders.update(order)
            await uow.commit()

            logger.info(
                "SHIPMENT USECASE | Shipment event processed and committed",
                order_id=str(order.id),
                new_status=order.status,
            )

            asyncio.create_task(
                self._send_notification_safe(
                    message=notification_message,
                    reference_id=str(order.id),
                    idempotency_key=str(idempotency_key),
                )
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
