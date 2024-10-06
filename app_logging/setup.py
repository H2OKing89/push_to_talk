# logger/setup.py

import logging
from logging.handlers import TimedRotatingFileHandler
from pythonjsonlogger import jsonlogger
import os
import asyncio

from .filters import ContextFilter
from .formatters import get_formatter
from .custom_handlers import get_file_handler, get_console_handler
from .cleanup import async_cleanup_old_logs
from .utils import sanitize_message

from config import load_config
from state import state

logger = logging.getLogger(__name__)

_logger_initialized = False
log_lock = asyncio.Lock()

def setup_logging(config: dict, correlation_id: str, trace_id: str) -> None:
    """
    Sets up advanced structured logging with context and cleanup.

    Args:
        config (dict): Configuration dictionary containing logging settings.
        correlation_id (str): Correlation ID for logging context.
        trace_id (str): Trace ID for logging context.
    """
    global _logger_initialized
    if _logger_initialized:
        return  # Logging is already configured

    logger = logging.getLogger()
    log_level_str = config.get('Logging', {}).get('log_level', 'DEBUG').upper()
    log_level = getattr(logging, log_level_str, logging.DEBUG)
    logger.setLevel(log_level)

    log_dir = os.path.abspath(config.get('Logging', {}).get('log_dir', 'logs/push_to_talk_logs'))
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'app.log')

   
