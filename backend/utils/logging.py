"""
Centralized logging setup for the backend.

Usage:
    from backend.utils.logging import get_logger
    logger = get_logger(__name__)
"""
import logging
import os


_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
_LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)


_configured = False


def _configure_root_logger() -> None:
    global _configured
    if _configured:
        return
    logging.basicConfig(level=_LOG_LEVEL, format=_LOG_FORMAT)
    # Reduce noise from third-party loggers if needed
    for noisy in ["sqlalchemy.engine", "urllib3", "openai", "httpx"]:
        logging.getLogger(noisy).setLevel(logging.WARNING)
    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Return a module-specific logger with centralized configuration."""
    _configure_root_logger()
    return logging.getLogger(name)


