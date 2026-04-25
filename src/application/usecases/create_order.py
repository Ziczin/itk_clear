import uuid
from typing import Any
from uuid import UUID

from src.application.ports.uow import IUoW
from src.domain.order import Order
from src.infrastructure.clients.catalog import CatalogClient, CatalogServiceError
from src.infrastructure.clients.notify import NotifyClient
from src.infrastructure.clients.payment import PaymentClient, PaymentServiceError
from src.utils.logger import logger


class CreateOrderUseCase:
    """Application service orchestrating order creation with validation."""

    def __init__(
        self,
        uow: IUoW,
        catalog_client: CatalogClient,
        payment_client: PaymentClient,
        notification_client: NotifyClient,
    ):
        """Inject required infrastructure and domain dependencies."""
        self.uow = uow
        self.catalog_client = catalog_client
        self.payment_client = payment_client
        self.notification_client = notification_client

    async def execute(
        self, user_id: str, item_id: UUID, quantity: int, idempotency_key: str
    ) -> Order:
        """Execute the complete order creation workflow."""
        logger.info(
            "CREATION USECASE | Initiating order creation flow",
            user_id=user_id,
            item_id=item_id,
            quantity=quantity,
            idempotency_key=idempotency_key,
        )

        async with self.uow as uow:
            existing_order = await uow.orders.get_by_idempotency_key(idempotency_key)

            if existing_order:
                logger.warning(
                    "USECASE CREATION | Duplicate request detected",
                    order_id=existing_order.id,
                    idempotency_key=idempotency_key,
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
                payment_result: dict[str, Any] = await self.payment_client.create(
                    order_id=str(order_id),
                    amount="100.00",
                    idempotency_key=str(idempotency_key),
                )
                payment_id_str = payment_result.get("id")
                if not payment_id_str:
                    raise PaymentServiceError("Payment ID missing in response")

                payment_id = UUID(payment_id_str)
            except PaymentServiceError as e:
                logger.error("Payment creation failed", error=str(e))
                raise

            order = Order(
                id=order_id,
                user_id=user_id,
                item_id=item_id,
                quantity=quantity,
                payment_id=payment_id,
            )

            await uow.orders.add(order=order)
            await uow.commit()

            logger.info(
                "CREATION USECASE | Order persisted successfully",
                order_id=str(order.id),
                payment_id=str(order.payment_id),
            )

            await self._send_notification_safe(
                message="Ваш заказ создан и ожидает оплаты",
                reference_id=str(order.id),
                idempotency_key=f"{idempotency_key}:new",
            )

            return order

    async def _send_notification_safe(
        self, message: str, reference_id: str, idempotency_key: str
    ) -> None:
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
