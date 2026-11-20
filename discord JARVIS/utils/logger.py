"""
JARVIS Logger

Configures Python logging for the bot.
Provides a centralized logger instance.
"""

import logging
import sys
from pathlib import Path


def setup_logging(log_file: str = "data/jarvis.log") -> logging.Logger:
    """
    Set up logging for JARVIS.
    Creates a log file and console handler.
    """
    # Ensure log directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Create logger
    logger = logging.getLogger("JARVIS")
    logger.setLevel(logging.INFO)

    # Prevent adding handlers multiple times
    if logger.handlers:
        return logger

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Get a logger instance.
    If name is provided, returns a child logger.
    """
    if name:
        return logging.getLogger(f"JARVIS.{name}")
    return logging.getLogger("JARVIS")
