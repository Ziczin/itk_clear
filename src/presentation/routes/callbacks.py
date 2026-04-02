from fastapi import APIRouter, Depends
from src.presentation.schemas import PaymentCallbackRequest
from src.application.usecases import ProcessPaymentCallbackUseCase
from src.utils.logger import logger
from src.presentation.dependencies import get_payment_callback_use_case

router = APIRouter(prefix="/api/orders", tags=["payments"])


@router.post("/payment-callback", status_code=200)
async def payment_callback(
    callback: PaymentCallbackRequest,
    use_case: ProcessPaymentCallbackUseCase = Depends(get_payment_callback_use_case),
):
    async with logger("Routes.PaymentCallback"):
        logger.info(
            "Handling Payment Callback",
            order_id=str(callback.order_id),
            status=callback.status,
        )
        try:
            await use_case.execute(
                order_id=callback.order_id,
                status=callback.status,
                payment_id=callback.payment_id,
                idempotency_key=callback.idempotency_key,
            )
            logger.info("Callback handled successfully")
            return {"status": "ok"}
        except Exception as e:
            logger.exception("Callback handling failed")
            return {"status": "error", "message": str(e)}
