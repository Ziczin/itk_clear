from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional


class CreateOrderReq(BaseModel):
    """Request payload for order creation endpoint."""

    user_id: str
    item_id: UUID
    quantity: int = Field(gt=0)
    idempotency_key: UUID


class OrderResp(BaseModel):
    """Response payload containing order details."""

    id: UUID
    user_id: str
    item_id: UUID
    quantity: int
    status: str
    created_at: str
    updated_at: str


class PaymentCallbackReq(BaseModel):
    """Request payload for payment gateway webhooks."""

    payment_id: UUID
    order_id: UUID
    status: str
    amount: str
    error_message: Optional[str] = None
    idempotency_key: UUID
