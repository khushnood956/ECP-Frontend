import logging
import sys
from contextvars import ContextVar
from typing import Optional
from app.core.config.settings import settings

# Context variable to store request ID
request_id_ctx_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class RequestIDFilter(logging.Filter):
    """
    Injects request_id into the log record if available.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        request_id = request_id_ctx_var.get()
        record.request_id = request_id if request_id else "N/A"
        return True


def get_logger(name: str) -> logging.Logger:
    """
    Creates and configures a centralized structured logger.
    
    Args:
        name (str): The name of the module/logger.
        
    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    
    # Avoid attaching multiple handlers if already configured
    if logger.handlers:
        return logger

    # Use application level logging based on environment
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)
    logger.propagate = False

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Standard formatter including module, level, timestamp, and request_id
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | [%(name)s] | [ReqID: %(request_id)s] | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    
    # Attach filter and handler
    console_handler.addFilter(RequestIDFilter())
    logger.addHandler(console_handler)

    return logger
