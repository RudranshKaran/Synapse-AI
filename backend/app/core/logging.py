"""Logging configuration for the Synapse AI backend.

Provides structured logging with consistent formatting
across all application components.
"""

import logging
import sys

from app.core.config import settings


def configure_logging() -> None:
    """Configure application-wide logging.

    Sets up structured logging with:
    - Consistent format including timestamp, level, and message
    - Stream handler writing to stdout
    - Configurable log level from settings
    """
    logger = logging.getLogger(settings.APP_NAME)
    logger.setLevel(settings.LOG_LEVEL.upper())

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(settings.LOG_LEVEL.upper())

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(handler)

    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given module name.

    Args:
        name: Usually __name__ from the calling module.

    Returns:
        Configured logger instance.
    """
    return logging.getLogger(f"{settings.APP_NAME}.{name}")
