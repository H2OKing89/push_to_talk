# gui/log_level_updater.py

import logging
from tkinter import messagebox

logger = logging.getLogger(__name__)

class LogLevelUpdater:
    def __init__(self, new_level, set_log_level_callback, correlation_id, trace_id):
        self.new_level = new_level
        self.set_log_level_callback = set_log_level_callback
        self.correlation_id = correlation_id
        self.trace_id = trace_id

    def update_log_level(self):
        if self.new_level:
            self.set_log_level_callback(self.new_level)
            logger.info(
                f"Log level changed to {self.new_level}",
                extra={'correlation_id': self.correlation_id, 'trace_id': self.trace_id}
            )
            messagebox.showinfo("Logging", f"Log level successfully changed to {self.new_level}.")
