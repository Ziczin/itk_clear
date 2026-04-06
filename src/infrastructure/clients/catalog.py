import aiohttp
from src.config import settings
from src.utils.logger import logger


class CatalogServiceError(Exception):
    """Raised when catalog service returns an error."""

    pass


class CatalogClient:
    """HTTP client for external catalog service integration."""

    def __init__(self, session: aiohttp.ClientSession):
        """Initialize client with aiohttp session."""
        self.session = session

    async def check_stock(self, item_id: str, quantity: int) -> dict:
        """Verify item availability against external inventory API."""
        url = f"{settings.CATALOG_URL}/api/catalog/items/{item_id}"
        headers = {"X-API-Key": settings.CAPASHINO_API_KEY}

        logger.debug("Requesting stock", url=url, item_id=item_id)

        async with self.session.get(url, headers=headers) as response:
            response_text = await response.text()

            if response.status == 404:
                logger.warning("Item not found in catalog", item_id=item_id)
                raise CatalogServiceError(f"Item {item_id} not found in catalog")

            if response.status != 200:
                logger.error(
                    "Catalog request failed",
                    status=response.status,
                    error=response_text,
                )
                raise CatalogServiceError(
                    f"Catalog API error: {response.status} - {response_text}"
                )

            data = await response.json()
            available_qty = data.get("available_qty", 0)

            logger.debug(
                "Stock received", available_qty=available_qty, requested=quantity
            )

            if available_qty < quantity:
                logger.warning(
                    "Insufficient stock",
                    available=available_qty,
                    requested=quantity,
                )
                raise CatalogServiceError("Insufficient stock")

            return data
