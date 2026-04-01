import json
import logging
import os
from datetime import datetime, timezone

from src.utils.logger.utils import ConsoleOutputType


class Formatter(logging.Formatter):
    """Форматтер для логов"""

    def __init__(
        self,
        project_root: str | None = None,
        console_output: str = ConsoleOutputType.PRETTY,
    ):
        super().__init__()
        self.project_root = project_root
        self.console_output = console_output

    def _get_relative_module_path(self, file_path: str) -> str:
        if self.project_root is None:
            return file_path

        try:
            abs_path = os.path.abspath(file_path)
            rel_path = os.path.relpath(abs_path, self.project_root)
            return rel_path.replace(os.sep, ".").replace(".py", "")
        except ValueError:
            return file_path

    def format(self, record: logging.LogRecord) -> str:
        call_file = record.pathname
        call_func = record.funcName
        call_line = record.lineno

        module_path = self._get_relative_module_path(call_file)
        place_str = f"{module_path}:{call_func}:{call_line}"

        if self.console_output == ConsoleOutputType.PLAIN:
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

            trace_str = ""
            if hasattr(record, "trace") and record.trace:
                context_id = record.trace.get("context", "")
                trace_stack = record.trace.get("trace", [])
                if trace_stack:
                    trace_str = f" [{context_id}] {' -> '.join(trace_stack)}"
                elif context_id:
                    trace_str = f" [{context_id}]"

            extra_str = ""
            extra_data = {}

            standard_attrs = {
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "exc_info",
                "exc_text",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "thread",
                "threadName",
                "funcName",
                "stack_info",
                "taskName",
                "trace",
                "console_output",
            }

            for key, value in record.__dict__.items():
                if key not in standard_attrs and not key.startswith("_"):
                    extra_data[key] = value

            if extra_data:
                extra_items = []
                for key, value in extra_data.items():
                    if key == "exception":
                        extra_items.append(f"\n  {value}")
                    else:
                        extra_items.append(f"{key}={value}")
                if extra_items:
                    extra_str = " " + " ".join(extra_items)

            if record.exc_info:
                exception_str = self.formatException(record.exc_info)
                extra_str = f"{extra_str}\n{exception_str}"

            return f"{timestamp} [{record.levelname}] {place_str}{trace_str} - {record.getMessage()}{extra_str}"

        log_entry = {
            "time": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "level": record.levelname,
            "place": place_str,
            "context": "",
            "trace": [],
            "data": {"message": record.getMessage(), "extra": {}},
        }

        if hasattr(record, "trace") and record.trace:
            log_entry["context"] = record.trace.get("context", "")
            log_entry["trace"] = record.trace.get("trace", [])

        standard_attrs = {
            "name",
            "msg",
            "args",
            "created",
            "filename",
            "exc_info",
            "exc_text",
            "levelname",
            "levelno",
            "lineno",
            "module",
            "msecs",
            "message",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "thread",
            "threadName",
            "funcName",
            "stack_info",
            "taskName",
            "trace",
            "console_output",
        }

        for key, value in record.__dict__.items():
            if key not in standard_attrs and not key.startswith("_"):
                log_entry["data"]["extra"][key] = value

        if record.exc_info:
            log_entry["data"]["extra"]["exception"] = self.formatException(
                record.exc_info
            )

        if self.console_output == ConsoleOutputType.PRETTY:
            return json.dumps(log_entry, ensure_ascii=False, indent=2, default=str)

        return json.dumps(log_entry, ensure_ascii=False, default=str)
