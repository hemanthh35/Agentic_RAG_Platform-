import logging
import sys
from contextvars import ContextVar
from typing import Optional

# Thread-safe ContextVar to store request ID for the current execution context
request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class RequestIdFilter(logging.Filter):
    """Logging filter to inject the current request ID from ContextVar into logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get() or "N/A"
        return True


def setup_logging(log_level: str = "INFO") -> None:
    """Configure structured logging using standard Python logging.

    Args:
        log_level: The logging level (e.g., "DEBUG", "INFO", "WARNING").
    """
    root_logger = logging.getLogger()
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(numeric_level)

    # Prevent duplicating handlers
    if root_logger.handlers:
        for handler in list(root_logger.handlers):
            root_logger.removeHandler(handler)

    # Setup standard stdout console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)

    # Structured format incorporating timestamp, severity, module name, and request context ID
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(name)s [%(request_id)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S %z",
    )
    console_handler.setFormatter(formatter)
    console_handler.addFilter(RequestIdFilter())

    root_logger.addHandler(console_handler)

    # Hook into Uvicorn loggers to maintain consistent formatting
    for uvicorn_logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uv_logger = logging.getLogger(uvicorn_logger_name)
        uv_logger.handlers = [console_handler]
        uv_logger.propagate = False
