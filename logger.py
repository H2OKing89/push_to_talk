# logger.py
import logging
import os  # Added import
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger
from utils import get_absolute_path
from config import load_config

def setup_logging(config, correlation_id):
    """Sets up structured JSON logging with log rotation and cleanup."""
    logger = logging.getLogger()
    log_level = getattr(logging, config['Logging'].get('log_level', 'INFO').upper(), logging.INFO)
    logger.setLevel(log_level)

    # Suppress matplotlib's DEBUG logs
    logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)

    # Create log directory if it doesn't exist
    log_dir = get_absolute_path(config['Logging'].get('log_dir', 'logs/push_to_logs'))
    os.makedirs(log_dir, exist_ok=True)

    # Log file path
    log_file = os.path.join(log_dir, 'push_to_talk.log')

    # Create log formatter with 'asctime' and 'levelname'
    log_formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s %(lineno)s %(funcName)s',
        rename_fields={
            'asctime': 'timestamp',
            'levelname': 'level',
            'name': 'logger',
            'message': 'message',
            'lineno': 'line_no',
            'funcName': 'function'
        }
    )

    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=config['LogCleanup'].get('max_log_files', 10)
    )
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)

    # Console handler
    if config['Logging'].get('log_to_console', True):
        console_log_level = getattr(logging, config['Logging'].get('console_log_level', 'INFO').upper(), logging.INFO)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_log_level)
        console_handler.setFormatter(log_formatter)
        logger.addHandler(console_handler)

    # Implement log cleanup
    if config['LogCleanup'].get('cleanup_enabled', True):
        retention_strategy = config['LogCleanup'].get('retention_strategy', 'time')
        retention_days = config['LogCleanup'].get('retention_days', 7)
        if retention_strategy == 'time':
            cleanup_logs_by_time(log_dir, retention_days, correlation_id)
        elif retention_strategy == 'size':
            cleanup_logs_by_size(log_dir, config['LogCleanup'].get('max_log_files', 10), correlation_id)

def cleanup_logs_by_time(log_dir, retention_days, correlation_id):
    """Deletes log files older than the retention period."""
    import time  # Import inside function to avoid circular imports
    now = time.time()
    for filename in os.listdir(log_dir):
        file_path = os.path.join(log_dir, filename)
        if os.path.isfile(file_path):
            file_mtime = os.path.getmtime(file_path)
            if (now - file_mtime) > (retention_days * 86400):  # 86400 seconds in a day
                try:
                    os.remove(file_path)
                    logging.info(f"Deleted old log file: {file_path}", extra={'correlation_id': correlation_id})
                except Exception as e:
                    logging.error(f"Failed to delete log file {file_path}: {e}", extra={'correlation_id': correlation_id})

def cleanup_logs_by_size(log_dir, max_log_files, correlation_id):
    """Keeps only the most recent 'max_log_files' log files."""
    try:
        log_files = sorted(
            [os.path.join(log_dir, f) for f in os.listdir(log_dir) if os.path.isfile(os.path.join(log_dir, f))],
            key=lambda x: os.path.getmtime(x),
            reverse=True
        )
        for log_file in log_files[max_log_files:]:
            os.remove(log_file)
            logging.info(f"Deleted excess log file: {log_file}", extra={'correlation_id': correlation_id})
    except Exception as e:
        logging.error(f"Error during log cleanup by size: {e}", extra={'correlation_id': correlation_id})
