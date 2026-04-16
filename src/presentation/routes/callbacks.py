from fastapi import APIRouter, Depends, status
from src.presentation.schemas.callback import PaymentCallbackRequest
from src.application.usecases.payment_callback import PaymentCallbackUseCase
from src.utils.logger import logger
from src.presentation.dependencies import provide_payment_callback_use_case

router = APIRouter(prefix="/api/orders", tags=["payments"])


@router.post("/payment-callback", status_code=status.HTTP_200_OK)
async def payment_callback(
    callback: PaymentCallbackRequest,
    use_case: PaymentCallbackUseCase = Depends(provide_payment_callback_use_case),
):
    """Process payment gateway webhook callbacks."""
    logger.debug("Route /payment-callback")
    logger.info(
        "Handling Payment Callback",
        order_id=str(callback.order_id),
        payment_status=callback.status,
        payment_id=str(callback.payment_id),
    )

    try:
        await use_case.execute(
            order_id=callback.order_id,
            payment_status=callback.status,
            payment_id=callback.payment_id,
            idempotency_key=callback.idempotency_key,
        )

        logger.info("Callback processed successfully", order_id=str(callback.order_id))
        logger.debug("Route /payment-callback returns 200")

        return {"status": "ok"}

    except Exception as e:
        logger.exception("Callback handling failed")
        logger.debug("Route /payment-callback returns 200 anyways")
        return {"status": "error", "message": str(e)}
