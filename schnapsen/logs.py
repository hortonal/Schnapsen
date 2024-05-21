"""Basic logging helpers."""
import logging
import sys


def basic_logger(level: int = logging.INFO) -> logging.Logger:
    """Setup and return a basic logger.

    Parameters
    ----------
    level : int
        Level to log at.

    Returns
    -------
    logging.Logger
        A configured logger instance.
    """
    logging.basicConfig(stream=sys.stderr)
    logger = logging.getLogger()
    logger.setLevel(level)
    return logger
