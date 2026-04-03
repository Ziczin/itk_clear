from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field


class OrderStatus(str, Enum):
    """Enumeration representing the lifecycle states of an order."""

    NEW = "NEW"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"


@dataclass
class Order:
    """Aggregate root encapsulating order state and business rules."""

    id: UUID = field(default_factory=uuid4)
    user_id: str = ""
    item_id: UUID = None
    quantity: int = 0
    status: OrderStatus = OrderStatus.NEW
    payment_id: UUID = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def transition_to_paid(self):
        """Update order status to reflect successful payment."""
        self.status = OrderStatus.PAID
        self.updated_at = datetime.utcnow()

    def transition_to_shipped(self):
        """Update order status to reflect successful shipment dispatch."""
        self.status = OrderStatus.SHIPPED
        self.updated_at = datetime.utcnow()

    def transition_to_cancelled(self):
        """Update order status to reflect cancellation."""
        self.status = OrderStatus.CANCELLED
        self.updated_at = datetime.utcnow()

    def bind_payment_id(self, payment_id: UUID):
        """Attach external payment identifier to the order entity."""
        self.payment_id = payment_id
