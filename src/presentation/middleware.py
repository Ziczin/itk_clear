from fastapi import Request
from src.utils.logger import set_request_id, clear_request_id


async def request_id_middleware(request: Request, call_next):
    """Middleware to set request ID for each incoming request."""
    # Get request_id from headers if provided, otherwise generate new one
    request_id = request.headers.get("x-request-id")
    set_request_id(request_id)
    
    try:
        response = await call_next(request)
        return response
    finally:
        clear_request_id()
