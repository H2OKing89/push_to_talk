# logger.py

import logging
import logging.handlers
from pythonjsonlogger import jsonlogger
from utils import get_absolute_path
import os
import threading
from datetime import datetime, timedelta
import re

# Set up module-specific logger
logger = logging.getLogger(__name__)

class ContextFilter(logging.Filter):
    """Injects contextual information into logs."""
    def __init__(self, correlation_id, trace_id):
        super().__init__()
        self.correlation_id = correlation_id
        self.trace_id = trace_id

    def filter(self, record):
        record.correlation_id = self.correlation_id
        record.trace_id = self.trace_id
        return True

log_lock = threading.Lock()
_logger_initialized = False

def sanitize_message(message):
    """Sanitizes sensitive information from log messages."""
    patterns = {
        'email': r'[\w\.-]+@[\w\.-]+',
        'credit_card': r'\b(?:\d[ -]*?){13,16}\b',
        # Add additional patterns as needed
    }
    for key, pattern in patterns.items():
        message = re.sub(pattern, f'[REDACTED {key.upper()}]', message, flags=re.IGNORECASE)
    return message

def cleanup_old_logs(log_dir, config):
    """Cleans up old log files based on retention policies."""
    try:
        if not config.get('LogCleanup', {}).get('cleanup_enabled', True):
            logger.debug("Log cleanup is disabled via configuration.")
            return

        retention_days = config.get('LogCleanup', {}).get('retention_days', 7)
        retention_strategy = config.get('LogCleanup', {}).get('retention_strategy', 'time')
        max_log_files = config.get('LogCleanup', {}).get('max_log_files', 10)

        now = datetime.now()
        cutoff_time = now - timedelta(days=retention_days)

        # List all log files in the directory
        log_files = [
            f for f in os.listdir(log_dir)
            if os.path.isfile(os.path.join(log_dir, f)) and f.endswith('.log')
        ]

        # Sort log files by modification time (oldest first)
        log_files.sort(key=lambda x: os.path.getmtime(os.path.join(log_dir, x)))

        # Retention based on time
        if retention_strategy == 'time':
            for log_file in log_files:
                file_path = os.path.join(log_dir, log_file)
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_mtime < cutoff_time:
                    os.remove(file_path)
                    logger.info(f"Deleted old log file: {file_path}")
        # Retention based on max number of log files
        elif retention_strategy == 'count':
            if len(log_files) > max_log_files:
                files_to_delete = log_files[:-max_log_files]
                for log_file in files_to_delete:
                    file_path = os.path.join(log_dir, log_file)
                    os.remove(file_path)
                    logger.info(f"Deleted log file to maintain max count: {file_path}")
    except Exception as e:
        logger.error(f"Error during log cleanup: {e}", exc_info=True)

def setup_logging(config, correlation_id, trace_id):
    """Sets up advanced structured logging with context and cleanup."""
    global _logger_initialized
    if _logger_initialized:
        return  # Logging is already configured

    with log_lock:
        logger = logging.getLogger()
        logger.setLevel(getattr(logging, config.get('Logging', {}).get('log_level', 'DEBUG').upper(), logging.DEBUG))
        log_dir = get_absolute_path(config.get('Logging', {}).get('log_dir', 'logs/push_to_talk_logs'))
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'app.log')

        # File Handler with TimedRotatingFileHandler for time-based rotation
        file_handler = logging.handlers.TimedRotatingFileHandler(
            log_file,
            when='midnight',
            interval=1,
            backupCount=config.get('LogCleanup', {}).get('max_log_files', 10),
            encoding='utf-8',
            delay=False,
            utc=False
        )
        file_handler.setLevel(getattr(logging, config.get('Logging', {}).get('log_level', 'DEBUG').upper(), logging.DEBUG))

        # Formatter
        if config.get('Logging', {}).get('log_format', 'json') == 'json':
            formatter = jsonlogger.JsonFormatter(
                fmt='%(asctime)s %(levelname)s %(name)s %(message)s correlation_id=%(correlation_id)s trace_id=%(trace_id)s',
                json_ensure_ascii=False
            )
        else:
            formatter = logging.Formatter(
                fmt='%(asctime)s - %(levelname)s - %(name)s - %(message)s - CorrelationID: %(correlation_id)s - TraceID: %(trace_id)s'
            )

        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console Handler
        if config.get('Logging', {}).get('log_to_console', False):
            console_handler = logging.StreamHandler()
            console_handler.setLevel(getattr(logging, config.get('Logging', {}).get('console_log_level', 'INFO').upper(), logging.INFO))
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        # Add Context Filter
        context_filter = ContextFilter(correlation_id, trace_id)
        logger.addFilter(context_filter)

        # Clean up old logs based on retention policy
        cleanup_old_logs(log_dir, config)

        _logger_initialized = True

def set_log_level(new_level):
    """Dynamically sets the log level."""
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, new_level.upper(), logging.DEBUG))
    for handler in logger.handlers:
        handler.setLevel(getattr(logging, new_level.upper(), logging.DEBUG))
    logger.info(f"Log level dynamically changed to {new_level.upper()}")
