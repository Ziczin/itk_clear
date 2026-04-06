from contextvars import ContextVar
from typing import Optional
import uuid


# Context variable for storing request UUID across async calls
_request_id: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def get_request_id() -> Optional[str]:
    """Get current request ID from context"""
    return _request_id.get()


def set_request_id(request_id: Optional[str] = None) -> str:
    """Set request ID in context. If not provided, generates a new UUID."""
    if request_id is None:
        request_id = str(uuid.uuid4())
    _request_id.set(request_id)
    return request_id


def clear_request_id() -> None:
    """Clear request ID from context"""
    _request_id.set(None)
