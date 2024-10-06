# gui/log_level_updater.py

import logging
from utils.logging_utils import sanitize_message

logger = logging.getLogger(__name__)

class LogLevelUpdater:
    def __init__(self, new_level, set_log_level_callback, correlation_id, trace_id):
        """
        Initializes the LogLevelUpdater.

        Args:
            new_level (str): The new log level to set.
            set_log_level_callback (callable): Callback to set the log level.
            correlation_id (str): Unique identifier for logging correlation.
            trace_id (str): Unique identifier for tracing.
        """
        self.new_level = new_level
        self.set_log_level_callback = set_log_level_callback
        self.correlation_id = correlation_id
        self.trace_id = trace_id

    def update_log_level(self):
        """
        Updates the log level using the provided callback.
        """
        if self.set_log_level_callback is not None:
            self.set_log_level_callback(self.new_level)
            logger.info(
                f"Log level updated to {self.new_level}.",
                extra={'correlation_id': self.correlation_id, 'trace_id': self.trace_id}
            )
        else:
            logger.warning(
                "set_log_level_callback is None. Log level was not updated.",
                extra={'correlation_id': self.correlation_id, 'trace_id': self.trace_id}
            )
