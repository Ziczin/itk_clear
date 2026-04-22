from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import (
    Response,
)

from src.utils.logger import clear_request_id, logger, set_request_id


class RequestIdMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware с request ID + логированием всех входящих запросов (включая 404)"""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request_id = request.headers.get("X-Request-ID")
        set_request_id(request_id)

        path = request.url.path
        method = request.method

        do_log = path not in ["/metrics", "/logs", "/openapi.json"]

        if do_log:
            logger.info(f"MIDDLEWARE | Incoming request | {method} {path}")

        try:
            response = await call_next(request)

            if do_log:
                logger.info(
                    f"MIDDLEWARE | Request completed | {method} {path} | status={response.status_code} | request_id={request_id}"
                )
            return response

        except Exception as exc:
            if do_log:
                logger.exception(
                    f"Request failed | {method} {path} | request_id={request_id}",
                    exc_info=exc,
                )
            raise
        finally:
            clear_request_id()
