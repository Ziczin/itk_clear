import aiohttp
import tenacity

from src.config import settings
from src.utils.logger import logger


class NotificationServiceError(Exception):
    """Raised when notification service returns an error."""

    pass


class NotifyClient:
    """HTTP client for user notification dispatch operations."""

    def __init__(self, session: aiohttp.ClientSession):
        """Initialize client with aiohttp session."""
        self.session = session

    @tenacity.retry(
        retry=tenacity.retry_if_exception_type(NotificationServiceError),
        stop=tenacity.stop_after_attempt(5),
        wait=tenacity.wait_incrementing(start=1, increment=1, max=20),
    )
    async def _send_notification_safe(
        self, url: str, payload: dict, headers: dict, reference_id: str
    ) -> bool:
        async with self.session.post(url, json=payload, headers=headers) as response:
            if response.status not in (200, 201):
                error_text = await response.text()
                logger.warning(
                    "NOTIFY CLIENT | Notification dispatch failed",
                    status=response.status,
                    error=error_text,
                    reference_id=reference_id,
                )
                raise NotificationServiceError(
                    f"status={response.status} body={error_text}"
                )
            logger.info("NOTIFY CLIENT | Notification sent", reference_id=reference_id)
            return True

    async def send(self, message: str, reference_id: str, idempotency_key: str) -> bool:
        """Dispatch a notification with guaranteed idempotency."""
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

        logger.debug(
            "NOTIFY CLIENT | Try to dispatch notification",
            url=url,
            payload=payload,
            headers=headers,
        )

        try:
            return await self._send_notification_safe(
                url, payload, headers, reference_id
            )
        except NotificationServiceError as e:
            logger.error(
                "NOTIFY CLIENT | Final failure after retries",
                error=str(e),
                reference_id=reference_id,
            )
            return False
        except aiohttp.ClientError as e:
            logger.warning(
                "NOTIFY CLIENT | Notification client connection error",
                error=str(e),
                reference_id=reference_id,
            )
            return False
        except Exception as e:
            logger.exception(
                "NOTIFY CLIENT | Notification sending failed unexpectedly",
                reference_id=reference_id,
                error=str(e),
            )
            return False
