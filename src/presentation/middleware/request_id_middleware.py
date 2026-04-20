from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from src.utils.logger import set_request_id, clear_request_id, get_request_id, logger


class RequestIdMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware that sets a unique request ID for each incoming HTTP request."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID")
        logger.debug("Incoming request X-Request-ID: %s", request_id)
        set_request_id(request_id)

        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = get_request_id()
            logger.debug("Outgoing response X-Request-ID: %s", response.headers.get("X-Request-ID"))
            return response
        finally:
            clear_request_id()
