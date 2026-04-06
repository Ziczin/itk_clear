from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class PaymentCallbackRequest(BaseModel):
    """Pydantic model validating payment gateway webhook payload."""

    payment_id: UUID
    order_id: UUID
    status: str
    amount: str
    error_message: Optional[str] = None
    idempotency_key: str
