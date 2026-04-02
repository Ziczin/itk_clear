from sqlalchemy import select, update
from src.application.ports import IOrderRepository, IOutboxRepository, IInboxRepository
from domain.models import Order, OutboxEntry, InboxEntry
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from src.infrastructure.database import Base
from src.utils.logger import logger


# --- ORM Models ---
class OrderDB(Base):
    __tablename__ = "orders"
    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    user_id = Column(String)
    item_id = Column(PG_UUID(as_uuid=True))
    quantity = Column(Integer)
    status = Column(String)
    payment_id = Column(PG_UUID(as_uuid=True), nullable=True)
    idempotency_key = Column(PG_UUID(as_uuid=True), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class OutboxDB(Base):
    __tablename__ = "outbox"
    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    event_type = Column(String)
    payload = Column(JSON)
    idempotency_key = Column(PG_UUID(as_uuid=True))
    status = Column(String, default="PENDING")


class InboxDB(Base):
    __tablename__ = "inbox"
    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    event_type = Column(String)
    idempotency_key = Column(PG_UUID(as_uuid=True), unique=True)
    processed_at = Column(DateTime, default=datetime.utcnow)


# --- Repositories ---


class SQLAlchemyOrderRepository(IOrderRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, order: Order, idempotency_key: UUID):
        logger.debug("Repo.AddingOrder", order_id=str(order.id))
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

    async def get(self, order_id: UUID) -> Order:
        logger.debug("Repo.GettingOrder", order_id=str(order_id))
        result = await self.session.get(OrderDB, order_id)
        return self._to_domain(result) if result else None

    async def update(self, order: Order):
        logger.debug("Repo.UpdatingOrder", order_id=str(order.id))
        stmt = (
            update(OrderDB)
            .where(OrderDB.id == order.id)
            .values(status=order.status.value, updated_at=order.updated_at)
        )
        await self.session.execute(stmt)

    async def get_by_idempotency_key(self, key: UUID) -> Order:
        logger.debug("Repo.GettingByIdempotency", key=str(key))
        result = await self.session.execute(
            select(OrderDB).where(OrderDB.idempotency_key == key)
        )
        db_order = result.scalar_one_or_none()
        return self._to_domain(db_order) if db_order else None

    def _to_domain(self, db_order: OrderDB) -> Order:
        return Order(
            id=db_order.id,
            user_id=db_order.user_id,
            item_id=db_order.item_id,
            quantity=db_order.quantity,
            status=db_order.status,
            payment_id=db_order.payment_id,
            created_at=db_order.created_at,
            updated_at=db_order.updated_at,
        )


class SQLAlchemyOutboxRepository(IOutboxRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, entry: OutboxEntry):
        db_entry = OutboxDB(
            id=entry.id,
            event_type=entry.event_type,
            payload=entry.payload,
            idempotency_key=entry.idempotency_key,
        )
        self.session.add(db_entry)

    async def get_pending(self, limit: int = 10):
        result = await self.session.execute(
            select(OutboxDB).where(OutboxDB.status == "PENDING").limit(limit)
        )
        return result.scalars().all()

    async def mark_as_published(self, entry_id: UUID):
        await self.session.execute(
            update(OutboxDB).where(OutboxDB.id == entry_id).values(status="PUBLISHED")
        )


class SQLAlchemyInboxRepository(IInboxRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, entry: InboxEntry):
        db_entry = InboxDB(id=entry.id, idempotency_key=entry.idempotency_key)
        self.session.add(db_entry)

    async def exists(self, idempotency_key: UUID) -> bool:
        result = await self.session.execute(
            select(InboxDB).where(InboxDB.idempotency_key == idempotency_key)
        )
        return result.scalar_one_or_none() is not None
