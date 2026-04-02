import aiohttp
from src.core.config import settings
from src.utils.logger import logger


class NotifyClient:
    """HTTP client for notification dispatch service."""

    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def send(self, msg: str, ref: str, key: str):
        """Dispatch user notification with idempotency guarantee."""
        url = f"{settings.NOTIFICATIONS_URL}"
        payload = {"message": msg, "reference_id": ref, "idempotency_key": key}
        headers = {
            "X-API-Key": settings.CAPASHINO_API_KEY,
            "Content-Type": "application/json",
        }
        try:
            async with self.session.post(url, json=payload, headers=headers) as r:
                if r.status not in (200, 201):
                    logger.warning("Notification dispatch failed", status=r.status)
        except Exception as e:
            logger.warning("Notification client exception", error=str(e))
