# app_logging/custom_handlers.py

import logging
from logging.handlers import TimedRotatingFileHandler
from .formatters import get_formatter
from utils.logging_utils import sanitize_message
from state import state

def get_file_handler(log_file: str, log_format: str) -> TimedRotatingFileHandler:
    """
    Creates and returns a TimedRotatingFileHandler.

    Args:
        log_file (str): Path to the log file.
        log_format (str): The format of the log messages ('json' or 'plain').

    Returns:
        TimedRotatingFileHandler: Configured file handler.
    """
    try:
        handler = TimedRotatingFileHandler(log_file, when='midnight', backupCount=7)
        formatter = get_formatter(log_format)
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)  # Set desired level
        return handler
    except Exception as e:
        sanitized_error = sanitize_message(str(e))
        logging.getLogger(__name__).error(
            f"Failed to create file handler: {sanitized_error}",
            extra={'correlation_id': state.correlation_id},
            exc_info=True
        )
        raise

def get_console_handler(log_format: str) -> logging.StreamHandler:
    """
    Creates and returns a StreamHandler for console output.

    Args:
        log_format (str): The format of the log messages ('json' or 'plain').

    Returns:
        StreamHandler: Configured console handler.
    """
    try:
        handler = logging.StreamHandler()
        formatter = get_formatter(log_format)
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)  # Set desired level
        return handler
    except Exception as e:
        sanitized_error = sanitize_message(str(e))
        logging.getLogger(__name__).error(
            f"Failed to create console handler: {sanitized_error}",
            extra={'correlation_id': state.correlation_id},
            exc_info=True
        )
        raise
