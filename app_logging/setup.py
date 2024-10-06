# app_logging/setup.py

import logging
from logging.handlers import TimedRotatingFileHandler
import os
import asyncio

from .filters import ContextFilter
from .formatters import get_formatter
from .custom_handlers import get_file_handler, get_console_handler
from .cleanup import async_cleanup_old_logs
from .utils import sanitize_message

from config import load_config
from config.schema import ConfigSchema  # Import ConfigSchema
from state import state

logger = logging.getLogger(__name__)

_logger_initialized = False
log_lock = asyncio.Lock()

def setup_logging(config: ConfigSchema, correlation_id: str, trace_id: str) -> None:
    """
    Sets up advanced structured logging with context and cleanup.

    Args:
        config (ConfigSchema): Configuration object containing logging settings.
        correlation_id (str): Correlation ID for logging context.
        trace_id (str): Trace ID for logging context.
    """
    global _logger_initialized
    if _logger_initialized:
        return  # Logging is already configured

    root_logger = logging.getLogger()

    # Access configuration attributes directly
    log_level_str = config.Logging.log_level.upper()
    log_level = getattr(logging, log_level_str, logging.DEBUG)
    root_logger.setLevel(log_level)

    log_dir = os.path.abspath(config.Logging.log_dir)
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'app.log')

    log_format = config.Logging.log_format

    # Get Formatter
    formatter = get_formatter(log_format)

    # Get File Handler
    file_handler = get_file_handler(log_file, log_format)
    root_logger.addHandler(file_handler)

    # Get Console Handler if enabled
    if config.Logging.log_to_console:
        console_handler = get_console_handler(log_format)
        root_logger.addHandler(console_handler)

    # Add Context Filter
    context_filter = ContextFilter(correlation_id, trace_id)
    root_logger.addFilter(context_filter)

    _logger_initialized = True
    logger.info("Logging is set up successfully.", extra={'correlation_id': correlation_id, 'trace_id': trace_id})

def set_log_level(level: str) -> None:
    """
    Sets the log level for the root logger.

    Args:
        level (str): The log level to set ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
    """
    root_logger = logging.getLogger()
    log_level = getattr(logging, level.upper(), logging.DEBUG)
    root_logger.setLevel(log_level)
    logger.info(
        f"Log level set to {level}",
        extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id}
    )
