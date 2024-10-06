# config/log_cleanup_config.py

from pydantic import BaseModel, validator

class LogCleanupConfig(BaseModel):
    cleanup_enabled: bool = True
    max_log_files: int = 10
    retention_days: int = 7
    retention_strategy: str = "time"

    @validator('retention_strategy')
    def validate_retention_strategy(cls, v):
        if v not in ['time', 'count']:
            raise ValueError("retention_strategy must be either 'time' or 'count'")
        return v
