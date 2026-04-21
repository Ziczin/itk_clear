from uuid import UUID

from pydantic import BaseModel


class PaymentCallbackRequest(BaseModel):
    """Pydantic model validating payment gateway webhook payload."""

    payment_id: UUID
    order_id: UUID
    status: str
    amount: str
    error_message: str | None = None
    idempotency_key: str | None = None
