from uuid import UUID

from src.external_api.api_router_template import APIRouterTemplate


class CapashinoAPI(APIRouterTemplate):
    def __init__(self, base_url: str, base_headers: dict | None = None):
        super().__init__(base_url, base_headers)

        self.catalog = self.api.at("catalog")
        self.catalog_items = self.catalog.at("items")

    async def get_item_from_catalog(self, item_id: str | UUID) -> dict:
        return await self.catalog_items.at(item_id).get()
