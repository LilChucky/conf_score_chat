"""
Shared logging configuration for the chat application.

Reads from environment variables (can be set in .env):
  LOG_LEVEL   - root log level: DEBUG | INFO | WARNING | ERROR  (default: INFO)
  LOG_FILE    - path to log file                                (default: logs/app.log)
  LOG_MAX_MB  - max size of one log file in MB before rotation  (default: 10)
  LOG_BACKUPS - number of rotated backup files to keep          (default: 5)

Import `get_logger` in any module to get a consistently formatted logger.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
_configured = False

# Third-party loggers to silence unless their level is explicitly needed
_NOISY_LOGGERS = ("httpx", "httpcore", "urllib3", "langchain", "openai")


def _parse_level(raw: str | None, default: int = logging.INFO) -> int:
    if not raw:
        return default
    level = logging.getLevelName(raw.upper())
    return level if isinstance(level, int) else default


def configure_logging(level: int | None = None) -> None:
    """
    Configure root logger once with console + rotating file handlers.
    Safe to call multiple times — only runs on first call.
    """
    global _configured
    if _configured:
        return

    # ── Settings from env ───────────────────────────────────
    effective_level = level or _parse_level(os.getenv("LOG_LEVEL"), logging.INFO)
    log_file = Path(os.getenv("LOG_FILE", "logs/app.log"))
    max_bytes = int(os.getenv("LOG_MAX_MB", "10")) * 1024 * 1024
    backup_count = int(os.getenv("LOG_BACKUPS", "5"))

    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)

    # ── Console handler ─────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # ── Rotating file handler ───────────────────────────────
    log_file.parent.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    # ── Root logger ──────────────────────────────────────────
    root = logging.getLogger()
    root.setLevel(effective_level)
    root.addHandler(console_handler)
    root.addHandler(file_handler)

    # Quiet noisy third-party loggers
    for noisy in _NOISY_LOGGERS:
        logging.getLogger(noisy).setLevel(logging.WARNING)

    _configured = True

    # First log line confirms settings
    _startup_log = logging.getLogger(__name__)
    _startup_log.info(
        "Logging initialised | level=%s | file=%s | max_mb=%s | backups=%s",
        logging.getLevelName(effective_level),
        log_file,
        os.getenv("LOG_MAX_MB", "10"),
        backup_count,
    )


def get_logger(name: str) -> logging.Logger:
    """Return a named logger, ensuring root is configured."""
    configure_logging()
    return logging.getLogger(name)
