import logging
import os
from logging import Logger

from pythonjsonlogger import jsonlogger


def setup_logging() -> Logger:
    """Configure logging for the application"""
    logger = logging.getLogger()
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(log_level)

    # Remove existing handlers
    for handler in logger.handlers:
        logger.removeHandler(handler)

    # Create JSON formatter
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
