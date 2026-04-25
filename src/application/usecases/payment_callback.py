import logging
import uuid
from typing import Optional

from src.domain.entities.order import OrderStatus
from src.domain.exceptions import DomainException
from src.domain.repositories.order import OrderRepository
from src.domain.repositories.outbox import OutboxRepository
from src.domain.services.notification import NotificationService

from src.infrastructure.uow import UnitOfWork

logger = logging.getLogger(__name__)


class PaymentCallbackUseCase:
    def __init__(
        self,
        order_repo: OrderRepository,
        outbox_repo: OutboxRepository,
        notification_service: NotificationService,
        uow: UnitOfWork,
    ):
        self.order_repo = order_repo
        self.outbox_repo = outbox_repo
        self.notification_service = notification_service
        self.uow = uow

    async def execute(
        self,
        order_id: str,
        payment_id: str,
        payment_status: str,
        amount: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None:
        logger.info(
            "CALLBACK USECASE | Processing payment result",
            extra={
                "order_id": order_id,
                "payment_status": payment_status,
                "payment_id": payment_id,
            },
        )

        async with self.uow:
            order = await self.order_repo.get(order_id)
            if not order:
                raise DomainException(f"Order {order_id} not found")

            if payment_status == "succeeded":
                order.status = OrderStatus.PAID

                # Генерируем idempotency_key, если он не передан
                idempotency_key = str(uuid.uuid4())

                # Создаем событие для отправки в Kafka
                event_payload = {
                    "event_type": "order.paid",
                    "order_id": order.id,
                    "item_id": order.item_id,
                    "quantity": order.quantity,
                    "idempotency_key": idempotency_key,
                }

                # Сохраняем событие в outbox
                await self.outbox_repo.add(
                    event_type="order.paid",
                    payload=event_payload,
                    idempotency_key=idempotency_key,
                )

                logger.info(
                    "CALLBACK USECASE | Order marked paid and outbox record created",
                    extra={"order_id": order.id},
                )

                # Отправляем уведомление об успешной оплате
                await self.notification_service.send(
                    message="Ваш заказ успешно оплачен и готов к отправке",
                    reference_id=order.id,
                    idempotency_key=idempotency_key,
                )

            elif payment_status == "failed":
                order.status = OrderStatus.CANCELLED

                # Генерируем idempotency_key для уведомления об отмене
                idempotency_key = str(uuid.uuid4())

                reason = error_message or "Payment failed"

                # Отправляем уведомление об отмене
                await self.notification_service.send(
                    message=f"Ваш заказ отменен. Причина: {reason}",
                    reference_id=order.id,
                    idempotency_key=idempotency_key,
                )

                logger.info(
                    "CALLBACK USECASE | Order cancelled due to payment failure",
                    extra={"order_id": order.id, "reason": reason},
                )
            else:
                raise DomainException(f"Unknown payment status: {payment_status}")

            # Обновляем заказ в БД
            await self.order_repo.update(order)

        logger.info(
            "CALLBACK USECASE | Callback processing completed",
            extra={"order_id": order.id, "new_status": order.status},
        )
