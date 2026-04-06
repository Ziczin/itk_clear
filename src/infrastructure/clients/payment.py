import aiohttp
from src.config import settings
from src.utils.logger import logger


class PaymentServiceError(Exception):
    """Raised when payment service returns an error."""

    pass


class PaymentClient:
    """HTTP client for payment gateway communication."""

    def __init__(self, session: aiohttp.ClientSession):
        """Initialize client with aiohttp session."""
        self.session = session

    async def create(self, order_id: str, amount: str, idempotency_key: str) -> dict:
        """Initialize a payment session with the external provider."""
        async with logger("Client.Payment.Create"):
            callback_url = settings.PAYMENT_CALLBACK_URL
            url = f"{settings.PAYMENTS_URL}/api/payments"

            payload = {
                "order_id": order_id,
                "amount": amount,
                "callback_url": str(callback_url),
                "idempotency_key": idempotency_key,
            }

            headers = {
                "X-API-Key": settings.CAPASHINO_API_KEY,
                "Content-Type": "application/json",
            }

            logger.debug(
                "Requesting payment creation",
                order_id=order_id,
                callback_url=callback_url,
            )

            async with self.session.post(
                url, json=payload, headers=headers
            ) as response:
                response_text = await response.text()

                if response.status not in (200, 201):
                    logger.error(
                        "Payment request failed",
                        status=response.status,
                        error=response_text,
                    )
                    raise PaymentServiceError(
                        f"Payment API error: {response.status} - {response_text}"
                    )

                result = await response.json()

                logger.info("Payment created", payment_id=result.get("id"))

                return result
