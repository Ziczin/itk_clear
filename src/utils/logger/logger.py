import logging
import uuid
import sys
import os

from src.utils.logger.utils import LogContext, ConsoleOutputType
from src.utils.logger.formatter import Formatter


PROJECT_ROOT = os.getcwd()


class ContextLogger:
    """Основной класс для логирования с поддержкой контекста"""

    def __init__(
        self, level: str = "INFO", console_output: str = ConsoleOutputType.PRETTY
    ):
        if not ConsoleOutputType.is_valid(console_output):
            raise ValueError(
                f"console_output must be one of {ConsoleOutputType.values()}, got {console_output}"
            )

        self.logger = logging.getLogger("context_logger")
        self.logger.setLevel(getattr(logging, level.upper()))
        self.logger.handlers.clear()

        console_handler = logging.StreamHandler(sys.stdout)
        self.formatter = Formatter(
            project_root=PROJECT_ROOT, console_output=console_output
        )
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)

        self._context: LogContext | None = None
        self._sentry_handler: bool | None = None
        self._next_context_name: str | None = None
        self._console_output = console_output

    def __call__(self, name: str):
        self._next_context_name = name
        return self

    def add_sentry(self, dsn: str, **kwargs):
        try:
            import sentry_sdk
            from sentry_sdk.integrations.logging import LoggingIntegration

            sentry_sdk.init(
                dsn=dsn,
                integrations=[
                    LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)
                ],
                **kwargs,
            )
            self._sentry_handler = True
        except ImportError:
            raise ImportError("Установите sentry-sdk: pip install sentry-sdk")

    def _log(self, level: str, message: str, **kwargs):
        exc_info = kwargs.pop("exc_info", None)
        stack_info = kwargs.pop("stack_info", None)
        extra = kwargs.pop("extra", {})

        if self._context:
            extra["trace"] = self._context.to_dict()

        extra.update(kwargs)
        extra["console_output"] = self._console_output

        log_method = getattr(self.logger, level.lower())
        log_method(
            message, extra=extra, exc_info=exc_info, stack_info=stack_info, stacklevel=3
        )

    def debug(self, message: str, **kwargs):
        self._log("DEBUG", message, **kwargs)

    def info(self, message: str, **kwargs):
        self._log("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs):
        self._log("WARNING", message, **kwargs)

    def error(self, message: str, **kwargs):
        self._log("ERROR", message, **kwargs)

    def critical(self, message: str, **kwargs):
        self._log("CRITICAL", message, **kwargs)

    def exception(self, message: str, **kwargs):
        self._log("ERROR", message, exc_info=True, **kwargs)

    def _enter_context(self):
        if self._context is None:
            trace_id = str(uuid.uuid4())
            self._context = LogContext(trace_id=trace_id)

        context_name = (
            self._next_context_name or f"context_{len(self._context.trace_stack)}"
        )
        self._context.push_trace(context_name)
        self._next_context_name = None
        return self

    def _exit_context(self, exc_type, exc_val, exc_tb):
        if self._context:
            self._context.pop_trace()
            if not self._context.trace_stack:
                self._context = None

    def __enter__(self):
        return self._enter_context()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._exit_context(exc_type, exc_val, exc_tb)

    async def __aenter__(self):
        return self._enter_context()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._exit_context(exc_type, exc_val, exc_tb)

    def set_context(self, trace_id: str | None = None, **extra):
        if trace_id is None:
            trace_id = str(uuid.uuid4())

        if self._context is None:
            self._context = LogContext(trace_id=trace_id)
        else:
            self._context.trace_id = trace_id

        self._context.extra.update(extra)

    def clear_context(self):
        self._context = None


logger = ContextLogger()
