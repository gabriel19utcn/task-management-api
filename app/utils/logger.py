import logging
import os
import sys

# Get log level from environment or default to INFO
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Define log format
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] - %(message)s"

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logger.addHandler(console_handler)

# Prevent duplicate log messages
logger.propagate = False


def get_logger(name: str = None) -> logging.Logger:
    """Get the basic logger."""
    return logger
