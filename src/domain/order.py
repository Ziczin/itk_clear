from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4


def utc_datettime() -> datetime:
    return datetime.now(timezone.utc)


class OrderStatus(str, Enum):
    """Enumeration representing the lifecycle states of an order."""

    NEW = "NEW"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"


@dataclass
class Order:
    """Aggregate root encapsulating order state and business rules."""

    item_id: UUID
    payment_id: UUID
    id: UUID = field(default_factory=uuid4)
    user_id: str = ""
    quantity: int = 0
    status: OrderStatus = OrderStatus.NEW
    created_at: datetime = field(default_factory=utc_datettime)
    updated_at: datetime = field(default_factory=utc_datettime)

    def transition_to_paid(self):
        """Update order status to reflect successful payment."""
        self.status = OrderStatus.PAID
        self.updated_at = utc_datettime()

    def transition_to_shipped(self):
        """Update order status to reflect successful shipment dispatch."""
        self.status = OrderStatus.SHIPPED
        self.updated_at = utc_datettime()

    def transition_to_cancelled(self):
        """Update order status to reflect cancellation."""
        self.status = OrderStatus.CANCELLED
        self.updated_at = utc_datettime()

    def bind_payment_id(self, payment_id: UUID):
        """Attach external payment identifier to the order entity."""
        self.payment_id = payment_id
