from src.domain.inbox import InboxEntry
from src.application.ports.uow import IUoW
from src.application.ports.order_repo import OrderNotFoundError
from src.utils.logger import logger
from uuid import UUID
import asyncio


class ShipmentEventUseCase:
    """Application service for processing shipping service Kafka events."""

    def __init__(self, uow: IUoW, notification_client):
        """Inject transactional unit and notification dependencies."""
        self.uow = uow
        self.notification_client = notification_client

    async def execute(self, event_data: dict):
        """Consume shipment event and update order state idempotently."""
        async with logger("UC.ShipmentEvent.execute"):
            event_type = event_data.get("event_type")
            order_id = UUID(event_data.get("order_id"))
            idempotency_key = UUID(
                event_data.get("idempotency_key", event_data.get("shipment_id"))
            )

            logger.info(
                "Processing shipment event",
                event_type=event_type,
                order_id=str(order_id),
            )

            async with self.uow as uow:
                if await uow.inbox.exists(idempotency_key=idempotency_key):
                    logger.warning(
                        "Duplicate event skipped", event_key=str(idempotency_key)
                    )
                    return

                order = await uow.orders.get(order_id=order_id)
                if order is None:
                    raise OrderNotFoundError()

                if event_type == "order.shipped":
                    order.transition_to_shipped()
                    notification_message = "Ваш заказ отправлен в доставку"
                elif event_type == "order.cancelled":
                    order.transition_to_cancelled()
                    notification_message = f"Ваш заказ отменен. Причина: {event_data.get('reason', 'unknown')}"
                else:
                    notification_message = "Unknown shipment event"

                await uow.inbox.add(entry=InboxEntry(idempotency_key=idempotency_key))
                await uow.commit()

                logger.info(
                    "Shipment event processed and committed",
                    order_id=str(order.id),
                    new_status=order.status,
                )
                asyncio.create_task(
                    self.notification_client.send(
                        message=notification_message,
                        reference_id=str(order.id),
                        idempotency_key=str(idempotency_key),
                    )
                )
