from src.domain.models import Order
from src.application.ports.uow import IUoW
from src.application.ports.order_repo import IOrderRepo
from src.utils.logger import logger
from uuid import UUID
import asyncio


class CreateOrderUC:
    """Use case for order creation with external validation and payment init."""

    def __init__(self, uow: IUoW, catalog, payment, notify):
        """Initialize dependencies for order creation flow."""
        self.uow = uow
        self.catalog = catalog
        self.payment = payment
        self.notify = notify

    async def execute(self, uid: str, iid: UUID, qty: int, key: UUID):
        """Execute order creation sequence with stock check and payment setup."""

        async with logger("UC.CreateOrder.execute"):
            logger.info("Initiating order creation flow", user_id=uid, item_id=str(iid))

            async with self.uow as uow:
                existing = await uow.orders.get_by_key(key)

                if existing:
                    logger.warning(
                        "Duplicate request detected", existing_id=str(existing.id)
                    )
                    raise IOrderRepo.Duplicate("Idempotency key already used")
                
                await self.catalog.check_stock(str(iid), qty)

                pay_res = await self.payment.create(str(iid), "100.00", str(key))
                order = Order(user_id=uid, item_id=iid, quantity=qty)
                order.set_payment(pay_res["id"])

                await uow.orders.add(order, key)
                await uow.commit()

                logger.info(
                    "Order persisted successfully",
                    order_id=str(order.id),
                    payment_id=str(order.payment_id),
                )

                asyncio.create_task(
                    self.notify.send("Ваш заказ создан", str(order.id), str(key))
                )

                return order
