# config/logging_config.py

from pydantic import BaseModel, validator
from typing import Optional

class LoggingConfig(BaseModel):
    console_log_level: str = "INFO"
    enable_dynamic_log_level: bool = True
    log_dir: str = "logs/push_to_talk_logs"
    log_format: str = "json"
    log_level: str = "DEBUG"
    log_to_console: bool = False

    @validator('log_format')
    def validate_log_format(cls, v):
        if v not in ['json', 'plain']:
            raise ValueError("log_format must be either 'json' or 'plain'")
        return v

    @validator('console_log_level', 'log_level')
    def validate_log_levels(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v
