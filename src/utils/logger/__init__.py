from loguru import logger as _loguru_logger

from src.utils.context_vars import get_request_id, set_request_id, clear_request_id


def json_sink(message):
    """JSON sink for loguru with 2-space indentation"""
    import sys
    import json
    from datetime import datetime, timezone
    import os

    record = message.record

    # Get relative module path
    project_root = os.getcwd()
    try:
        abs_path = os.path.abspath(record["file"].path)
        rel_path = os.path.relpath(abs_path, project_root)
        place_str = (
            f"{rel_path.replace(os.sep, '.')}.py:{record['function']}:{record['line']}"
        )
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

    sys.stderr.write(
        json.dumps(log_entry, ensure_ascii=False, indent=2, default=str) + "\n"
    )


# Configure loguru with JSON sink
_loguru_logger.remove()
_loguru_logger.add(
    json_sink,
    level="INFO",
    colorize=False,
)

logger = _loguru_logger

__all__ = ["logger", "get_request_id", "set_request_id", "clear_request_id"]
