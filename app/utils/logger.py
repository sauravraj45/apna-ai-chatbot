"""
Centralized logging configuration.

Usage:
    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Something happened")

Design notes:
- Never log raw request/response bodies, JWTs, passwords, or full user
  objects. Use `redact()` when you must include user-derived data in a
  log line.
"""

import logging
import sys
from typing import Any

from app.config.settings import get_settings

_CONFIGURED = False


def _configure_root_logger() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    settings = get_settings()
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(settings.LOG_LEVEL.upper())
    root.handlers = [handler]

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger for the given module name."""
    _configure_root_logger()
    return logging.getLogger(name)


def redact(value: Any, keep: int = 4) -> str:
    """Mask a sensitive value, keeping only the last `keep` characters.

    Useful for logging things like "a JWT was received" without leaking the
    token itself: redact(token) -> "****ab12"
    """
    text = str(value)
    if len(text) <= keep:
        return "*" * len(text)
    return "*" * (len(text) - keep) + text[-keep:]
