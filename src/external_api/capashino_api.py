from uuid import UUID
from abc import ABC

from src.external_api.api_router_template import APIRouterTemplate


class ICapashinoAPI(ABC):
    class ItemNotFoundInCatalog(Exception): ...

    class BadRequest(Exception): ...

    async def get_item_from_catalog(self, item_id: str | UUID) -> dict: ...


class CapashinoAPI(APIRouterTemplate, ICapashinoAPI):
    def __init__(self, base_url: str, base_headers: dict | None = None):
        super().__init__(base_url, base_headers)

        self.catalog = self.api.at("catalog")
        self.catalog_items = self.catalog.at("items")

    async def get_item_from_catalog(self, item_id: str | UUID) -> dict:
        result = await self.catalog_items.at(item_id).get(self._with_status_code)
        code, data = result["status_code"], result["data"]
        if code == 200:
            return data

        raise {404: self.ItemNotFoundInCatalog(f"Item with {item_id} not founded")}[
            code
        ]
