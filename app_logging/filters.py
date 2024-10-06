# logger/filters.py

import logging

class ContextFilter(logging.Filter):
    """Injects contextual information into logs."""
    def __init__(self, correlation_id: str, trace_id: str):
        super().__init__()
        self.correlation_id = correlation_id
        self.trace_id = trace_id

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = self.correlation_id
        record.trace_id = self.trace_id
        return True
