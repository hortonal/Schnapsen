"""Basic logging helpers."""
import logging
import sys
from typing import Optional


def basic_logger(level: Optional[int] = logging.INFO) -> logging.Logger:
    """Setup and return a basic logger.

    Args:
        level (Optional[int], optional): Level to log at.. Defaults to logging.INFO.

    Returns:
        logging.Logger: A configured logger instance.
    """
    logging.basicConfig(stream=sys.stderr)
    logger = logging.getLogger()
    logger.setLevel(level)
    return logger
