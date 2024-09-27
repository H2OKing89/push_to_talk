# logger.py
import logging
from pythonjsonlogger import jsonlogger
import os
from utils import get_absolute_path

def setup_logging(config, correlation_id):
    """Sets up logging with JSON formatting and log rotation."""
    log_level = config.get('Logging', {}).get('log_level', 'DEBUG')
    log_file = config.get('log_file', 'app.log')
    log_dir = config.get('Logging', {}).get('log_dir', 'logs/push_to_logs')
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_file)

    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper(), logging.DEBUG))

    # Create file handler
    fh = logging.FileHandler(log_path)
    fh.setLevel(getattr(logging, log_level.upper(), logging.DEBUG))

    # Create formatter
    formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s correlation_id=%(correlation_id)s')
    fh.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(fh)

    # Optionally add console handler
    if config.get('Logging', {}).get('log_to_console', False):
        ch = logging.StreamHandler()
        ch.setLevel(getattr(logging, config.get('Logging', {}).get('console_log_level', 'INFO').upper(), logging.INFO))
        ch.setFormatter(formatter)
        logger.addHandler(ch)
