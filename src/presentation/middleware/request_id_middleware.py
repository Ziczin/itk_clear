import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from src.utils.logger import set_request_id, clear_request_id, get_request_id

logger = logging.getLogger(__name__)


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID")
        set_request_id(request_id)

        body = await request.body()
        request._receive = lambda: {"type": "http.request", "body": body}
        logger.debug(f"REQUEST BODY: {body.decode('utf-8', errors='replace')}")

        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = get_request_id()

            response_body = b"".join([chunk async for chunk in response.body_iterator])
            response = Response(
                response_body,
                response.status_code,
                response.headers,
                response.media_type,
            )
            logger.debug(
                f"RESPONSE BODY: {response_body.decode('utf-8', errors='replace')}"
            )

            return response
        finally:
            clear_request_id()
