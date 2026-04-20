from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from src.utils.logger import set_request_id, clear_request_id, get_request_id, logger


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        set_request_id(request.headers.get("X-Request-ID"))
        try:
            req_id = get_request_id()

            req_body = await request.body()
            logger.info(
                f"{request.method} {request.url.path}",
                request_body=req_body.decode("utf-8", errors="replace"),
            )

            response = await call_next(request)

            resp_body = b""
            async for chunk in response.body_iterator:
                resp_body += chunk

            logger.info(
                f"{request.method} {request.url.path} [{response.status_code}]",
                response_body=resp_body.decode("utf-8", errors="replace"),
            )

            response.headers["X-Request-ID"] = req_id
            return Response(
                content=resp_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )
        finally:
            clear_request_id()
