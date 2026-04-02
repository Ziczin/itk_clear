from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from src.presentation.schemas import CreateOrderReq, OrderResp, PaymentCallbackReq
from src.application.usecases.create_order import CreateOrderUC
from src.application.usecases.get_order import GetOrderUC
from src.application.usecases.payment_callback import PaymentCallbackUC
from src.utils.logger import logger
from src.presentation.dependencies import (
    get_create_uc,
    get_get_order_uc,
    get_callback_uc,
)

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("", status_code=201, response_model=OrderResp)
async def create(req: CreateOrderReq, uc: CreateOrderUC = Depends(get_create_uc)):
    """Handle incoming order creation requests."""
    async with logger("Routes.create_order"):
        try:
            order = await uc.execute(
                req.user_id, req.item_id, req.quantity, req.idempotency_key
            )
            logger.info("Order created successfully", order_id=str(order.id))
            return OrderResp(
                id=order.id,
                user_id=order.user_id,
                item_id=order.item_id,
                quantity=order.quantity,
                status=order.status.value,
                created_at=order.created_at.isoformat(),
                updated_at=order.updated_at.isoformat(),
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))


@router.get("/{order_id}", response_model=OrderResp)
async def get_by_id(order_id: UUID, uc: GetOrderUC = Depends(get_get_order_uc)):
    """Retrieve order details by unique identifier."""
    async with logger("Routes.get_order"):
        try:
            order = await uc.execute(order_id)
            logger.info("Order retrieved successfully", order_id=str(order_id))
            return OrderResp(
                id=order.id,
                user_id=order.user_id,
                item_id=order.item_id,
                quantity=order.quantity,
                status=order.status.value,
                created_at=order.created_at.isoformat(),
                updated_at=order.updated_at.isoformat(),
            )
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))


@router.post("/payment-callback", status_code=200)
async def callback(
    req: PaymentCallbackReq, uc: PaymentCallbackUC = Depends(get_callback_uc)
):
    """Handle payment gateway webhook callbacks."""
    async with logger("Routes.payment_callback"):
        try:
            await uc.execute(
                req.order_id, req.status, req.payment_id, req.idempotency_key
            )
            logger.info("Callback processed successfully", order_id=str(req.order_id))
            return {"status": "ok"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
