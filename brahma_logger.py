"""
Brahma Echo — Logging System
Provides crash logging and debug output for the packaged application.
Logs go to %LOCALAPPDATA%/Brahma Echo/logs/ (always writable).
"""

import sys
import os
import logging
import traceback
from pathlib import Path
from datetime import datetime


def _get_log_dir() -> Path:
    """Get the log directory, writable in all modes."""
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        log_dir = Path(local_app_data) / "Brahma Echo" / "logs"
    elif getattr(sys, "frozen", False):
        log_dir = Path(sys.executable).parent / "logs"
    else:
        log_dir = Path(__file__).resolve().parent / "logs"

    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def get_log_file() -> Path:
    """Get the current log file path."""
    return _get_log_dir() / "brahma_echo.log"


def get_crash_log_file() -> Path:
    """Get the crash log file path."""
    return _get_log_dir() / "crash_log.txt"


def is_debug_mode() -> bool:
    """Check if --debug flag was passed or BRAHMA_DEBUG env var is set."""
    return "--debug" in sys.argv or os.environ.get("BRAHMA_DEBUG", "").lower() in ("1", "true", "yes")


def setup_logging(debug: bool = False) -> logging.Logger:
    """Configure and return the application logger."""
    log_level = logging.DEBUG if (debug or is_debug_mode()) else logging.INFO
    log_file = get_log_file()

    logger = logging.getLogger("brahma_echo")
    logger.setLevel(log_level)
    logger.handlers.clear()

    # File handler (always on)
    file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler (only in debug mode or dev)
    if debug or is_debug_mode() or not getattr(sys, "frozen", False):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(file_formatter)
        logger.addHandler(console_handler)

    logger.info(f"Logging initialized — level: {logging.getLevelName(log_level)}")
    logger.info(f"Log file: {log_file}")

    return logger


def log_crash(exc_type, exc_value, exc_traceback):
    """Write an unhandled exception to the crash log."""
    crash_file = get_crash_log_file()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(crash_file, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"CRASH: {timestamp}\n")
        f.write(f"{'='*60}\n")
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)
        f.write(f"\n")

    # Also print to stderr
    traceback.print_exception(exc_type, exc_value, exc_traceback)


def install_crash_handler():
    """Install a global exception handler that logs crashes."""
    sys.excepthook = log_crash
