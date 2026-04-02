from fastapi import APIRouter, Depends, HTTPException
from src.presentation.schemas import CreateOrderRequest, OrderResponse
from src.application.usecases import CreateOrderUseCase
from src.utils.logger import logger
from src.presentation.dependencies import get_create_order_use_case

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("", status_code=201, response_model=OrderResponse)
async def create_order(
    request: CreateOrderRequest,
    use_case: CreateOrderUseCase = Depends(get_create_order_use_case),
):
    async with logger("Routes.CreateOrder"):
        logger.info("Handling CreateOrder request", user_id=request.user_id)
        try:
            order = await use_case.execute(
                user_id=request.user_id,
                item_id=request.item_id,
                quantity=request.quantity,
                idempotency_key=request.idempotency_key,
            )

            logger.info("Order creation successful", order_id=str(order.id))

            return OrderResponse(
                id=order.id,
                user_id=order.user_id,
                item_id=order.item_id,
                quantity=order.quantity,
                status=order.status,
                created_at=order.created_at.isoformat(),
                updated_at=order.updated_at.isoformat(),
            )
        except Exception as e:
            logger.exception("Order creation failed")
            raise HTTPException(status_code=400, detail=str(e))
