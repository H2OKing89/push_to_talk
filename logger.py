# logger.py
import logging
from pythonjsonlogger import jsonlogger
import os
from logging.handlers import RotatingFileHandler
from utils import get_absolute_path

def setup_logging(config, correlation_id):
    """Sets up logging with JSON formatting and log rotation."""
    log_level = config.get('Logging', {}).get('log_level', 'DEBUG')
    log_dir = config.get('Logging', {}).get('log_dir', 'logs/push_to_logs')
    os.makedirs(log_dir, exist_ok=True)

    # Set up rotating file handlers
    log_path_info = os.path.join(log_dir, 'info.log')
    log_path_error = os.path.join(log_dir, 'error.log')

    # File handler for info logs
    info_handler = RotatingFileHandler(log_path_info, maxBytes=5000000, backupCount=5)
    info_handler.setLevel(logging.INFO)

    # File handler for error logs
    error_handler = RotatingFileHandler(log_path_error, maxBytes=5000000, backupCount=5)
    error_handler.setLevel(logging.ERROR)

    # JSON formatter
    formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s correlation_id=%(correlation_id)s')
    info_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper(), logging.DEBUG))

    # Add handlers
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)

    # Optionally add console handler
    if config.get('Logging', {}).get('log_to_console', False):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
