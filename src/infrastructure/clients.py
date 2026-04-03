import aiohttp
from src.domain.exceptions import (
    CatalogServiceError,
    PaymentServiceError,
    NotificationServiceError,
)
from src.utils.logger import logger
from src.core.config import settings


class CatalogClient:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def check_stock(self, item_id: str, quantity: int):
        async with logger("Client.Catalog.CheckStock"):
            url = f"{settings.CATALOG_URL}/items/{item_id}"
            headers = {"X-API-Key": settings.CAPASHINO_API_KEY}

            logger.debug("Requesting stock", url=url)
            async with self.session.get(url, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()

                    logger.error(
                        "Catalog request failed",
                        status=response.status,
                        error=error_text,
                    )

                    raise CatalogServiceError(f"Catalog error: {error_text}")

                data = await response.json()
                logger.debug("Stock received", available=data.get("available_qty"))

                if data.get("available_qty", 0) < quantity:
                    logger.warning(
                        "Insufficient stock returned by client",
                        available=data.get("available_qty"),
                        requested=quantity,
                    )
                    raise CatalogServiceError("Insufficient stock")

                return data


class PaymentClient:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def create_payment(self, order_id: str, amount: str, idempotency_key: str):
        async with logger("Client.Payment.Create"):
            url = f"{settings.PAYMENTS_URL}/api/payments"  # Path corrected based on assignment usually
            payload = {
                "order_id": order_id,
                "amount": amount,
                "callback_url": str(settings.PAYMENT_CALLBACK_URL),
                "idempotency_key": idempotency_key,
            }
            headers = {
                "X-API-Key": settings.CAPASHINO_API_KEY,
                "Content-Type": "application/json",
            }

            logger.debug("Requesting payment creation", order_id=order_id)

            async with self.session.post(
                url, json=payload, headers=headers
            ) as response:
                if response.status not in (200, 201):
                    error_text = await response.text()

                    logger.error(
                        "Payment request failed",
                        status=response.status,
                        error=error_text,
                    )

                    raise PaymentServiceError(f"Payment error: {error_text}")

                result = await response.json()

                logger.info("Payment created", payment_id=result.get("id"))

                return result


class NotificationClient:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def send_notification(
        self, message: str, reference_id: str, idempotency_key: str
    ):
        async with logger("Client.Notification.Send"):
            url = f"{settings.NOTIFICATIONS_URL}/api/notifications"
            payload = {
                "message": message,
                "reference_id": reference_id,
                "idempotency_key": idempotency_key,
            }
            headers = {
                "X-API-Key": settings.CAPASHINO_API_KEY,
                "Content-Type": "application/json",
            }

            try:
                async with self.session.post(
                    url, json=payload, headers=headers
                ) as response:
                    if response.status not in (200, 201):
                        logger.error(
                            "Notification request failed", status=response.status
                        )
                        raise NotificationServiceError(
                            f"Notification error: {await response.text()}"
                        )
                    logger.info("Notification sent", reference_id=reference_id)

            except Exception:
                logger.exception(
                    "Notification sending failed", reference_id=reference_id
                )
