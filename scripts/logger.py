#!/usr/bin/env python3
"""
Logging configuration for zlibrary-to-notebooklm.

Provides emoji-prefixed logging for visual feedback in terminal output.
"""
import logging
import sys
from typing import Optional


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Create a logger with console output.

    Args:
        name: Logger name
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


class EmojiLogger:
    """
    Logger with emoji prefixes for visual feedback.

    Usage:
        logger = EmojiLogger("my_module")
        logger.info("Processing file")    # Output: "Processing file"
        logger.success("Done!")           # Output: "Done!"
        logger.error("Failed!")           # Output: "Failed!"
    """

    def __init__(self, name: str, level: int = logging.INFO):
        """
        Initialize emoji logger.

        Args:
            name: Logger name
            level: Logging level
        """
        self._logger = setup_logger(name, level)

    def info(self, msg: str) -> None:
        """Log info message."""
        self._logger.info(msg)

    def success(self, msg: str) -> None:
        """Log success message."""
        self._logger.info(msg)

    def warning(self, msg: str) -> None:
        """Log warning message."""
        self._logger.warning(msg)

    def error(self, msg: str) -> None:
        """Log error message."""
        self._logger.error(msg)

    def debug(self, msg: str) -> None:
        """Log debug message."""
        self._logger.debug(msg)

    def section(self, title: str, width: int = 70) -> None:
        """Print a section header."""
        self._logger.info("=" * width)
        self._logger.info(title)
        self._logger.info("=" * width)

    def step(self, step_num: int, total: int, msg: str) -> None:
        """Log a step in a multi-step process."""
        self._logger.info(f"Step {step_num}/{total}: {msg}")

    def progress(self, current: int, msg: Optional[str] = None) -> None:
        """Log progress update."""
        if msg:
            self._logger.info(f"   {msg}... {current}s")
        else:
            self._logger.info(f"   Waiting... {current}s")


# Convenience function to get a logger instance
def get_logger(name: str) -> EmojiLogger:
    """
    Get an EmojiLogger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        EmojiLogger instance
    """
    return EmojiLogger(name)
