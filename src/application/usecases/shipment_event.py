from src.domain.models import InboxEntry
from src.application.ports.uow import IUoW
from src.application.ports.order_repo import IOrderRepo
from src.utils.logger import logger
from uuid import UUID
import asyncio


class ShipmentEventUC:
    """Use case for processing shipping service Kafka events."""

    def __init__(self, uow: IUoW, notify):
        """Initialize dependencies for shipment event handling."""
        self.uow = uow
        self.notify = notify

    async def execute(self, data: dict):
        """Consume shipment event and update order state idempotently."""
        async with logger("UC.ShipmentEvent.execute"):
            etype = data.get("event_type")
            oid = UUID(data.get("order_id"))
            key = UUID(data.get("idempotency_key", data.get("shipment_id")))
            logger.info("Processing shipment event", type=etype, order_id=str(oid))
            async with self.uow as uow:
                if await uow.inbox.exists(key):
                    logger.warning("Duplicate event skipped", event_key=str(key))
                    return
                order = await uow.orders.get(oid)
                if not order:
                    raise IOrderRepo.NotFound("Order missing for shipment update")
                if etype == "order.shipped":
                    order.mark_shipped()
                    msg = "Ваш заказ отправлен в доставку"
                elif etype == "order.cancelled":
                    order.mark_cancelled()
                    msg = f"Ваш заказ отменен. Причина: {data.get('reason', 'unknown')}"
                else:
                    msg = "Unknown shipment event"
                await uow.inbox.add(InboxEntry(idempotency_key=key))
                await uow.commit()
                logger.info(
                    "Shipment event processed and committed",
                    order_id=str(order.id),
                    new_status=order.status.value,
                )
                asyncio.create_task(self.notify.send(msg, str(order.id), str(key)))
