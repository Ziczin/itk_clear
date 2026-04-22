from uuid import UUID

from sqlalchemy import select
from sqlalchemy import update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.order_repo import IOrderRepo
from src.domain.order import Order
from src.infrastructure.models.order import OrderDB
from src.utils.logger import logger


class OrderRepo(IOrderRepo):
    """SQLAlchemy implementation of the order repository interface."""

    def __init__(self) -> None:
        self.session: AsyncSession | None = None

    async def add(self, order: Order, idempotency_key: str | None = None) -> None:
        """Stage a new order entity for insertion into the database."""
        if self.session is None:
            raise RuntimeError("Session not initialized")

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

    async def get(self, order_id: UUID) -> Order | None:
        """Fetch an order entity by its primary key identifier."""
        if self.session is None:
            raise RuntimeError("Session not initialized")

        logger.info("ORDER REPO | Getting order", order_id=order_id)
        result = await self.session.get(OrderDB, order_id)
        return self._map_to_domain(result) if result else None

    async def update(self, order: Order) -> None:
        """Apply status and timestamp updates to an existing database record."""
        if self.session is None:
            raise RuntimeError("Session not initialized")

        logger.info("ORDER REPO | Updating order", id=order.id)
        statement = (
            sa_update(OrderDB)
            .where(OrderDB.id == order.id)
            .values(status=order.status.value, updated_at=order.updated_at)
        )
        await self.session.execute(statement)

    async def get_by_idempotency_key(self, key: str) -> Order | None:
        """Retrieve an order using its unique idempotency constraint key."""
        if self.session is None:
            raise RuntimeError("Session not initialized")

        logger.info(
            "ORDER REPO | Getting order by idempotency key",
            idempotency_key=key,
        )
        result = await self.session.execute(
            select(OrderDB).where(OrderDB.idempotency_key == key)
        )
        db_order = result.scalar_one_or_none()
        logger.info(
            f"ORDER REPO | {'Successful' if db_order else 'Failed'} getting order by idempotency key",
            idempotency_key=key,
        )

        return self._map_to_domain(db_order) if db_order else None

    def _map_to_domain(self, db_model: OrderDB) -> Order:
        """Convert a SQLAlchemy ORM model to a domain order entity."""
        from src.domain.order import OrderStatus

        return Order(
            id=db_model.id,  # type: ignore[arg-type]
            user_id=db_model.user_id,  # type: ignore[arg-type]
            item_id=db_model.item_id,  # type: ignore[arg-type]
            quantity=db_model.quantity,  # type: ignore[arg-type]
            status=OrderStatus(db_model.status),  # type: ignore[arg-type]
            payment_id=db_model.payment_id,  # type: ignore[arg-type]
            created_at=db_model.created_at,  # type: ignore[arg-type]
            updated_at=db_model.updated_at,  # type: ignore[arg-type]
        )
