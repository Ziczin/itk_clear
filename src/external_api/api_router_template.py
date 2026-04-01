from src.utils.request_builder import RequestBuilder, QueryConfig


class APIRouterTemplate:
    def __init__(self, base_url: str, base_headers: dict | None = None):
        self._base = RequestBuilder().at(base_url).via(base_headers)
        self._with_status_code = QueryConfig(with_status_code=True)
        self._with_trailing_slash = QueryConfig(trailing_slash=True)

        self.empty = self._base.view()
        self.api = self.base.at("api")

    def _get_timeout_config(self, seconds: float) -> QueryConfig:
        return QueryConfig(timeout=seconds)

    def _get_retries_config(self, count: int) -> QueryConfig:
        return QueryConfig(max_retries=count)
