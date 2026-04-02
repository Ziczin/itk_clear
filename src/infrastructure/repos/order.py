from sqlalchemy import select, update
from src.application.ports.order_repo import IOrderRepo
from src.infrastructure.orm_models import OrderDB
from src.domain.models import Order
from uuid import UUID


class OrderRepo(IOrderRepo):
    """SQLAlchemy implementation of order repository interface."""

    def __init__(self):
        self.session = None

    async def add(self, order, key: UUID):
        """Insert new order entity into database session."""
        db_order = OrderDB(
            id=order.id,
            user_id=order.user_id,
            item_id=order.item_id,
            quantity=order.quantity,
            status=order.status.value,
            payment_id=order.payment_id,
            idempotency_key=key,
        )
        self.session.add(db_order)

    async def get(self, oid: UUID) -> object:
        """Fetch order by primary key identifier."""
        res = await self.session.get(OrderDB, oid)
        return self._to_domain(res) if res else None

    async def update(self, order):
        """Apply status and timestamp updates to existing record."""
        stmt = (
            update(OrderDB)
            .where(OrderDB.id == order.id)
            .values(status=order.status.value, updated_at=order.updated_at)
        )
        await self.session.execute(stmt)

    async def get_by_key(self, key: UUID) -> object:
        """Retrieve order using idempotency key constraint."""
        res = await self.session.execute(
            select(OrderDB).where(OrderDB.idempotency_key == key)
        )
        db = res.scalar_one_or_none()
        return self._to_domain(db) if db else None

    def _to_domain(self, db):
        """Convert SQLAlchemy model to domain entity."""
        return Order(
            id=db.id,
            user_id=db.user_id,
            item_id=db.item_id,
            quantity=db.quantity,
            status=db.status,
            payment_id=db.payment_id,
            created_at=db.created_at,
            updated_at=db.updated_at,
        )
