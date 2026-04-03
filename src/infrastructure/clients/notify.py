import aiohttp
from src.config import settings
from src.utils.logger import logger


class NotifyClient:
    """HTTP client handling user notification dispatch operations."""

    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def send(self, message: str, reference_id: str, idempotency_key: str):
        """Dispatch a notification with guaranteed idempotency."""
        url = f"{settings.NOTIFICATIONS_URL}"
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
                    logger.warning(
                        "Notification dispatch failed", status=response.status
                    )
        except Exception as exception:
            logger.warning("Notification client exception", error=str(exception))
