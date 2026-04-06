from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from src.presentation.schemas.order import CreateOrderRequest, OrderResponse
from src.presentation.schemas.callback import PaymentCallbackRequest
from src.application.usecases.create_order import CreateOrderUseCase
from src.application.usecases.get_order import GetOrderUseCase
from src.application.usecases.payment_callback import PaymentCallbackUseCase
from src.utils.context_vars import logger
from src.presentation.dependencies import (
    provide_create_order_use_case,
    provide_get_order_use_case,
    provide_payment_callback_use_case,
)


order_router = APIRouter(prefix="/api/orders", tags=["orders"])


@order_router.post("", status_code=201, response_model=OrderResponse)
async def handle_create_order(
    request: CreateOrderRequest,
    use_case: CreateOrderUseCase = Depends(provide_create_order_use_case),
):
    """Process incoming order creation requests."""
    async with logger("Routes.create_order"):
        try:
            order = await use_case.execute(
                user_id=request.user_id,
                item_id=request.item_id,
                quantity=request.quantity,
                idempotency_key=request.idempotency_key,
            )
            logger.info("Order created successfully", order_id=str(order.id))

            return OrderResponse(
                id=order.id,
                user_id=order.user_id,
                item_id=order.item_id,
                quantity=order.quantity,
                status=order.status.value,
                created_at=order.created_at.isoformat(),
                updated_at=order.updated_at.isoformat(),
            )
        except Exception as exception:
            raise HTTPException(status_code=400, detail=str(exception))


@order_router.get("/{order_id}", response_model=OrderResponse)
async def handle_get_order(
    order_id: UUID, use_case: GetOrderUseCase = Depends(provide_get_order_use_case)
):
    """Retrieve order details by unique identifier."""
    async with logger("Routes.get_order"):
        try:
            order = await use_case.execute(order_id=order_id)
            logger.info("Order retrieved successfully", order_id=str(order_id))

            return OrderResponse(
                id=order.id,
                user_id=order.user_id,
                item_id=order.item_id,
                quantity=order.quantity,
                status=order.status.value,
                created_at=order.created_at.isoformat(),
                updated_at=order.updated_at.isoformat(),
            )
        except Exception as exception:
            raise HTTPException(status_code=404, detail=str(exception))


@order_router.post("/payment-callback", status_code=200)
async def handle_payment_callback(
    request: PaymentCallbackRequest,
    use_case: PaymentCallbackUseCase = Depends(provide_payment_callback_use_case),
):
    """Process payment gateway webhook callbacks."""
    async with logger("Routes.payment_callback"):
        try:
            await use_case.execute(
                order_id=request.order_id,
                payment_status=request.status,
                payment_id=request.payment_id,
                idempotency_key=request.idempotency_key,
            )
            logger.info(
                "Callback processed successfully", order_id=str(request.order_id)
            )
            return {"status": "ok"}
        except Exception as exception:
            return {"status": "error", "message": str(exception)}
