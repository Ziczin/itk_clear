from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field


class OrderStatus(str, Enum):
    """Order lifecycle states enumeration."""

    NEW = "NEW"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"


@dataclass
class Order:
    """Aggregate root representing customer order state."""

    id: UUID = field(default_factory=uuid4)
    user_id: str = ""
    item_id: UUID = None
    quantity: int = 0
    status: OrderStatus = OrderStatus.NEW
    payment_id: UUID = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def mark_paid(self):
        self.status = OrderStatus.PAID

    def mark_shipped(self):
        self.status = OrderStatus.SHIPPED

    def mark_cancelled(self):
        self.status = OrderStatus.CANCELLED

    def set_payment(self, pid: UUID):
        self.payment_id = pid


@dataclass
class OutboxEntry:
    """Reliable event storage for asynchronous publishing."""

    id: UUID = field(default_factory=uuid4)
    event_type: str = ""
    payload: dict = None
    idempotency_key: UUID = None
    status: str = "PENDING"


@dataclass
class InboxEntry:
    """Idempotency tracking record for processed events."""

    id: UUID = field(default_factory=uuid4)
    idempotency_key: UUID = None
