from pydantic import BaseModel, Field
from uuid import UUID


class CreateOrderRequest(BaseModel):
    """Pydantic model validating order creation request payload."""

    user_id: str
    item_id: UUID
    quantity: int = Field(gt=0)
    idempotency_key: str


class OrderResponse(BaseModel):
    """Pydantic model structuring order details in HTTP response."""

    id: UUID
    user_id: str
    item_id: UUID
    quantity: int
    status: str
    created_at: str
    updated_at: str
