# logger/cleanup.py

import os
import logging
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import asyncio

from .utils import sanitize_message

logger = logging.getLogger(__name__)

def cleanup_old_logs(log_dir: str, config: dict) -> None:
    """
    Cleans up old log files based on retention policies.

    Args:
        log_dir (str): Directory where log files are stored.
        config (dict): Configuration dictionary containing cleanup policies.
    """
    try:
        if not config.get('LogCleanup', {}).get('cleanup_enabled', True):
            logger.debug("Log cleanup is disabled via configuration.")
            return

        retention_strategy = config.get('LogCleanup', {}).get('retention_strategy', 'time')
        retention_days = config.get('LogCleanup', {}).get('retention_days', 7)
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

        if retention_strategy == 'time':
            for log_file in log_files:
                file_path = os.path.join(log_dir, log_file)
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_mtime < cutoff_time:
                    os.remove(file_path)
                    logger.info(f"Deleted old log file: {file_path}")
        elif retention_strategy == 'count':
            if len(log_files) > max_log_files:
                files_to_delete = log_files[:-max_log_files]
                for log_file in files_to_delete:
                    file_path = os.path.join(log_dir, log_file)
                    os.remove(file_path)
                    logger.info(f"Deleted log file to maintain max count: {file_path}")
    except Exception as e:
        logger.error(f"Error during log cleanup: {sanitize_message(str(e))}", exc_info=True)

async def async_cleanup_old_logs(loop: asyncio.AbstractEventLoop, log_dir: str, config: dict) -> None:
    """
    Asynchronously cleans up old log files.

    Args:
        loop (asyncio.AbstractEventLoop): The event loop.
        log_dir (str): Directory where log files are stored.
        config (dict): Configuration dictionary containing cleanup policies.
    """
    with ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, cleanup_old_logs, log_dir, config)
