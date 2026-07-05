"""logging.py — structured logging configuration for the Lexara AI core.

Call `configure_logging()` once at application startup (e.g. in FastAPI
lifespan or the CLI entrypoint) to apply the standard log format across
all core modules.
"""
from __future__ import annotations

import logging


def configure_logging(level: str = "INFO") -> None:
    """Configure root logger with a standard format.

    Args:
        level: Log level string (e.g. "INFO", "DEBUG", "WARNING").
    """
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(levelname)-8s %(name)s — %(message)s",
    )
    logging.getLogger("core").setLevel(getattr(logging, level.upper(), logging.INFO))


def get_logger(name: str) -> logging.Logger:
    """Return a named logger for a core module.

    Usage:
        from core.telemetry.logging import get_logger
        log = get_logger(__name__)
    """
    return logging.getLogger(name)
