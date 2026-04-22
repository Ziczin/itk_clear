from fastapi import APIRouter, Depends, status

from src.application.usecases.payment_callback import PaymentCallbackUseCase
from src.presentation.dependencies import provide_payment_callback_use_case
from src.presentation.schemas.callback import PaymentCallbackRequest
from src.utils.logger import logger

router = APIRouter(prefix="/api/orders", tags=["payments"])


@router.post("/payment-callback", status_code=status.HTTP_200_OK)
async def payment_callback(
    callback: PaymentCallbackRequest,
    use_case: PaymentCallbackUseCase = Depends(provide_payment_callback_use_case),
):
    """Process payment gateway webhook callbacks."""
    logger.info(
        "CALLBACK ROUTE | Handling Route /payment-callback",
        order_id=str(callback.order_id),
        payment_status=callback.status,
        payment_id=str(callback.payment_id),
    )

    try:
        await use_case.execute(
            order_id=callback.order_id,
            payment_status=callback.status,
            payment_id=callback.payment_id,
            idempotency_key=callback.idempotency_key
            or "Backend: There is no idempotensy key provided",
        )

        logger.info(
            "CALLBACK ROUTE | Callback processed successfully",
            order_id=str(callback.order_id),
        )
        logger.debug("CALLBACK ROUTE | Route /payment-callback returns 200")

        return {"status": "ok"}

    except Exception as e:
        logger.exception("CALLBACK ROUTE | Callback handling failed")
        logger.debug("CALLBACK ROUTE | Route /payment-callback returns 200 anyways")
        return {"status": "error", "message": str(e)}
