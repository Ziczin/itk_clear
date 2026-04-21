from sqlalchemy import select, update
from src.application.ports.order_repo import IOrderRepo
from src.infrastructure.models.order import OrderDB
from src.domain.order import Order
from uuid import UUID
from src.utils.logger import logger


class OrderRepo(IOrderRepo):
    """SQLAlchemy implementation of the order repository interface."""

    def __init__(self):
        self.session = None

    async def add(self, order, idempotency_key: str):
        """Stage a new order entity for insertion into the database."""
        logger.info(
            "ORDER REPO | Adding order",
            id=order.id,
            user_id=order.user_id,
            item_id=order.item_id,
            quantity=order.quantity,
            status=order.status.value,
            payment_id=order.payment_id,
            idempotency_key=idempotency_key,
        )
        db_order = OrderDB(
            id=order.id,
            user_id=order.user_id,
            item_id=order.item_id,
            quantity=order.quantity,
            status=order.status.value,
            payment_id=order.payment_id,
            idempotency_key=idempotency_key,
        )
        self.session.add(db_order)

    async def get(self, order_id: UUID):
        """Fetch an order entity by its primary key identifier."""
        logger.info("ORDER REPO | Getting order", order_id=order_id)
        result = await self.session.get(OrderDB, order_id)
        return self._map_to_domain(result) if result else None

    async def update(self, order):
        """Apply status and timestamp updates to an existing database record."""
        logger.info("ORDER REPO | Updating order", id=order.id)
        statement = (
            update(OrderDB)
            .where(OrderDB.id == order.id)
            .values(status=order.status.value, updated_at=order.updated_at)
        )
        await self.session.execute(statement)

    async def get_by_idempotency_key(self, idempotency_key: str) -> Order | None:
        """Retrieve an order using its unique idempotency constraint key."""
        logger.info(
            "ORDER REPO | Getting order by idempotency key",
            idempotency_key=idempotency_key,
        )
        result = await self.session.execute(
            select(OrderDB).where(OrderDB.idempotency_key == idempotency_key)
        )
        db_order = result.scalar_one_or_none()
        logger.info(
            f"ORDER REPO | {'Successful' if db_order else 'Failed'} getting order by idempotency key",
            idempotency_key=idempotency_key,
        )

        return self._map_to_domain(db_order) if db_order else None

    def _map_to_domain(self, db_model) -> Order:
        """Convert a SQLAlchemy ORM model to a domain order entity."""
        return Order(
            id=db_model.id,
            user_id=db_model.user_id,
            item_id=db_model.item_id,
            quantity=db_model.quantity,
            status=db_model.status,
            payment_id=db_model.payment_id,
            created_at=db_model.created_at,
            updated_at=db_model.updated_at,
        )
