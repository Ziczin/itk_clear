# logger_config.py
import json
import os
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import List, Optional

from loguru import logger as _loguru_logger

_request_id: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def get_request_id() -> Optional[str]:
    return _request_id.get()


def set_request_id(request_id: Optional[str] = None) -> str:
    if request_id is None:
        request_id = str(uuid.uuid4())
    _request_id.set(request_id)
    return request_id


def clear_request_id() -> None:
    _request_id.set(None)


_logs_jsonl: List[str] = []


def get_logs_jsonl() -> List[str]:
    """Возвращает копию списка логов в формате JSONL (каждая строка — JSON)."""
    return _logs_jsonl.copy()


def clear_logs_jsonl() -> None:
    """Очищает накопленные логи."""
    _logs_jsonl.clear()


def json_sink(message):
    record = message.record
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

    extra_data = record.get("extra", {})
    for key, value in extra_data.items():
        if not key.startswith("_"):
            log_entry["data"]["extra"][key] = value

    if record.get("exception"):
        log_entry["data"]["extra"]["exception"] = record["exception"]

    sys.stderr.write(
        json.dumps(log_entry, ensure_ascii=False, indent=2, default=str) + "\n"
    )


def memory_jsonl_sink(message):
    """Формирует компактный JSON и добавляет его в список _logs_jsonl (как строку JSONL)."""
    record = message.record
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

    extra_data = record.get("extra", {})
    for key, value in extra_data.items():
        if not key.startswith("_"):
            log_entry["data"]["extra"][key] = value

    if record.get("exception"):
        log_entry["data"]["extra"]["exception"] = record["exception"]

    json_line = json.dumps(log_entry, ensure_ascii=False, default=str)
    _logs_jsonl.append(json_line)


# _loguru_logger.remove()
# _loguru_logger.add(json_sink, level="INFO", colorize=False)
_loguru_logger.add(memory_jsonl_sink, level="DEBUG")

logger = _loguru_logger

__all__ = [
    "logger",
    "get_request_id",
    "set_request_id",
    "clear_request_id",
    "get_logs_jsonl",
    "clear_logs_jsonl",
]
