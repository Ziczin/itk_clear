import json
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from src.utils.logger import set_request_id, clear_request_id, get_request_id, logger


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        set_request_id(request.headers.get("X-Request-ID"))
        try:
            response = await call_next(request)
            if request.url.path not in ("/logs", "/metrics"):
                req_b = await request.body()
                resp_b = b"".join([c async for c in response.body_iterator])
                logger.info(
                    f"{request.method} {request.url.path}",
                    request_body=json.loads(req_b),
                )
                logger.info(
                    f"{request.method} {request.url.path} [{response.status_code}]",
                    response_body=json.loads(resp_b),
                )
                response.headers["X-Request-ID"] = get_request_id()
                return Response(
                    content=resp_b,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type,
                )
            response.headers["X-Request-ID"] = get_request_id()
            return response
        finally:
            clear_request_id()
