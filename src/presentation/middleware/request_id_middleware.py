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
            response: Response = await call_next(request)

            if do_log:
                response_body = b""
                async for chunk in response.body_iterator:  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType, reportAttributeAccessIssue]
                    response_body += chunk  # pyright: ignore[reportUnknownVariableType]

                response = Response(
                    content=response_body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type,
                )

                if response_body:
                    logger.info(
                        f"MIDDLEWARE | Request completed | {method} {path} with code {response.status_code}",
                        body=response_body.decode("utf-8", errors="replace"),  # pyright: ignore[reportUnknownMemberType]
                    )

            return response

        except Exception as exc:
            if do_log:
                logger.exception(
                    f"Request failed | {method} {path}",
                    exc_info=exc,
                )
            raise
        finally:
            clear_request_id()
