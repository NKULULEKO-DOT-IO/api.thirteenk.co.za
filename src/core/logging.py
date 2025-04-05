import logging
import sys
from pydantic import AnyHttpUrl
from typing import Any, Dict, List, Optional, Union

from src.core.config import get_settings

settings = get_settings()


def setup_logging():
    """Configure logging for the application."""
    log_level = getattr(logging, settings.LOG_LEVEL)

    # Create logger
    logger = logging.getLogger("thirteenk")
    logger.setLevel(log_level)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    return logger


# Create a logger instance
logger = setup_logging()