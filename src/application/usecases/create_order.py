import asyncio
import uuid
from uuid import UUID

from src.application.ports.uow import IUoW
from src.domain.order import Order
from src.infrastructure.clients.catalog import CatalogServiceError
from src.infrastructure.clients.payment import PaymentServiceError
from src.utils.logger import logger


class CreateOrderUseCase:
    """Application service orchestrating order creation with validation."""

    def __init__(self, uow: IUoW, catalog_client, payment_client, notification_client):
        """Inject required infrastructure and domain dependencies."""
        self.uow = uow
        self.catalog_client = catalog_client
        self.payment_client = payment_client
        self.notification_client = notification_client

    async def execute(
        self, user_id: str, item_id: UUID, quantity: int, idempotency_key: str
    ):
        """Execute the complete order creation workflow."""
        logger.info(
            "Initiating order creation flow",
            user_id=user_id,
            item_id=str(item_id),
            quantity=quantity,
            idempotency_key=str(idempotency_key),
        )

        async with self.uow as uow:
            existing_order = await uow.orders.get_by_idempotency_key(idempotency_key)

            if existing_order:
                logger.warning(
                    "Duplicate request detected",
                    order_id=str(existing_order.id),
                    idempotency_key=str(idempotency_key),
                )
                return existing_order

            try:
                await self.catalog_client.check_stock(
                    item_id=str(item_id), quantity=quantity
                )
            except CatalogServiceError as e:
                logger.error("Catalog check failed", error=str(e))
                raise

            order_id = uuid.uuid4()
            try:
                payment_result = await self.payment_client.create(
                    order_id=str(order_id),  # str(item_id),
                    amount="100.00",
                    idempotency_key=str(idempotency_key),
                )
                payment_id = UUID(payment_result["id"])
            except PaymentServiceError as e:
                logger.error("Payment creation failed", error=str(e))
                raise

            order = Order(
                id=order_id, user_id=user_id, item_id=item_id, quantity=quantity
            )
            order.bind_payment_id(payment_id=payment_id)

            await uow.orders.add(order=order, idempotency_key=idempotency_key)
            await uow.commit()

            logger.info(
                "Order persisted successfully",
                order_id=str(order.id),
                payment_id=str(order.payment_id),
            )

            asyncio.create_task(
                self._send_notification_safe(
                    message="Ваш заказ создан и ожидает оплаты",
                    reference_id=str(order.id),
                    idempotency_key=str(idempotency_key),
                )
            )

            return order

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
