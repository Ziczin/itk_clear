import aiohttp
from src.config import settings


class CatalogClient:
    """HTTP client facilitating external catalog service integration."""

    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def check_stock(self, item_id: str, quantity: int):
        """Verify item availability against external inventory API."""
        url = f"{settings.CATALOG_URL}/items/{item_id}"
        headers = {"X-API-Key": settings.CAPASHINO_API_KEY}

        async with self.session.get(url, headers=headers) as response:
            if response.status != 200:
                raise ValueError(f"Catalog API error: {response.status}")

            data = await response.json()
            if data.get("available_qty", 0) < quantity:
                raise ValueError("Insufficient stock")

            return data
