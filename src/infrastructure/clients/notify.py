import aiohttp
from src.config import settings
from src.utils.context_vars import logger


class NotificationServiceError(Exception):
    """Raised when notification service returns an error."""

    pass


class NotifyClient:
    """HTTP client for user notification dispatch operations."""

    def __init__(self, session: aiohttp.ClientSession):
        """Initialize client with aiohttp session."""
        self.session = session

    async def send(self, message: str, reference_id: str, idempotency_key: str) -> bool:
        """Dispatch a notification with guaranteed idempotency."""
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
                        error_text = await response.text()
                        logger.warning(
                            "Notification dispatch failed",
                            status=response.status,
                            error=error_text,
                            reference_id=reference_id,
                        )
                        return False

                    logger.info("Notification sent", reference_id=reference_id)

                    return True

            except aiohttp.ClientError as e:
                logger.warning(
                    "Notification client connection error",
                    error=str(e),
                    reference_id=reference_id,
                )
                return False

            except Exception:
                logger.exception(
                    "Notification sending failed unexpectedly",
                    reference_id=reference_id,
                )
                return False
