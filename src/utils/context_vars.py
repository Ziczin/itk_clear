from contextvars import ContextVar
from typing import Optional
import uuid
import sys
import json
from datetime import datetime, timezone
import os

from loguru import logger as _loguru_logger


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


def json_sink(message):
    """JSON sink for loguru with 2-space indentation"""
    record = message.record

    # Get relative module path
    project_root = os.getcwd()
    try:
        abs_path = os.path.abspath(record["file"].path)
        rel_path = os.path.relpath(abs_path, project_root)
        place_str = f"{rel_path.replace(os.sep, '.')}.py:{record['function']}:{record['line']}"
    except (ValueError, KeyError):
        place_str = f"{record.get('file', {}).get('path', 'unknown')}:{record.get('function', 'unknown')}:{record.get('line', 'unknown')}"

    log_entry = {
        "time": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "level": record["level"].name,
        "place": place_str,
        "request_id": get_request_id(),
        "data": {"message": record["message"], "extra": {}},
    }

    # Add extra fields from record
    extra_data = record.get("extra", {})
    for key, value in extra_data.items():
        if not key.startswith("_"):
            log_entry["data"]["extra"][key] = value

    # Format exception if present
    if record.get("exception"):
        log_entry["data"]["extra"]["exception"] = record["exception"]

    sys.stderr.write(json.dumps(log_entry, ensure_ascii=False, indent=2, default=str) + "\n")


# Configure loguru with JSON sink
_loguru_logger.remove()
_loguru_logger.add(
    json_sink,
    level="INFO",
    colorize=False,
)

logger = _loguru_logger

__all__ = ["logger", "get_request_id", "set_request_id", "clear_request_id"]
