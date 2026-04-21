from pydantic import BaseModel


class PaymentCallbackRequest(BaseModel):
    """Pydantic model validating payment gateway webhook payload."""

    payment_id: str
    order_id: str
    status: str
    amount: str
    error_message: str | None = None
    idempotency_key: str
