import aiohttp
from src.core.config import settings


class PaymentClient:
    """HTTP client for payment gateway integration."""

    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def create(self, oid: str, amount: str, key: str):
        """Initialize payment session with external payment provider."""
        url = f"{settings.PAYMENTS_URL}"
        payload = {
            "order_id": oid,
            "amount": amount,
            "callback_url": str(settings.PAYMENT_CALLBACK_URL),
            "idempotency_key": key,
        }
        headers = {
            "X-API-Key": settings.CAPASHINO_API_KEY,
            "Content-Type": "application/json",
        }
        async with self.session.post(url, json=payload, headers=headers) as r:
            if r.status not in (200, 201):
                raise ValueError(f"Payment API error: {r.status}")
            return await r.json()
