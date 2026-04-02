import aiohttp
from src.core.config import settings


class CatalogClient:
    """HTTP client for external catalog service integration."""

    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def check_stock(self, iid: str, qty: int):
        """Verify item availability against external inventory API."""
        url = f"{settings.CATALOG_URL}/items/{iid}"
        headers = {"X-API-Key": settings.CAPASHINO_API_KEY}
        async with self.session.get(url, headers=headers) as r:
            if r.status != 200:
                raise ValueError(f"Catalog API error: {r.status}")
            data = await r.json()
            if data.get("available_qty", 0) < qty:
                raise ValueError("Insufficient stock")
            return data
