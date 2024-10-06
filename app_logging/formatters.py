# app_logging/formatters.py

import logging
from pythonjsonlogger import jsonlogger

def get_formatter(log_format: str):
    """
    Returns a logging formatter based on the specified format.

    Args:
        log_format (str): The desired log format ('json' or 'plain').

    Returns:
        logging.Formatter: Configured formatter instance.
    """
    if log_format.lower() == 'json':
        # Define JSON formatter with timestamp and message
        return jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s'
        )
    elif log_format.lower() == 'plain':
        # Define plain text formatter
        return logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    else:
        # Default to plain text formatter if unknown format is provided
        return logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
