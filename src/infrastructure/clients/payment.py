import aiohttp
from src.config import settings


class PaymentClient:
    """HTTP client managing payment gateway communication."""

    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def create(self, order_id: str, amount: str, idempotency_key: str):
        """Initialize a payment session with the external provider."""
        url = f"{settings.PAYMENTS_URL}"
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

        async with self.session.post(url, json=payload, headers=headers) as response:
            if response.status not in (200, 201):
                raise ValueError(f"Payment API error: {response.status}")

            return await response.json()
