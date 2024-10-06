# config/schemas.py

from pydantic import BaseModel, Field
from typing import List, Optional
import sounddevice as sd

# Ensure that these imports point to existing modules or adjust as necessary
# If these modules don't exist, you should define them or remove these imports
from .logging_config import LoggingConfig
from .log_cleanup_config import LogCleanupConfig
from .gui_settings_config import GUISettingsConfig
from .model_support_config import ModelSupportConfig

# config/schema.py

class ModelSupportSchema(BaseModel):
    default_model: str = "turbo"  # Set default to 'turbo' if desired
    available_models: List[str] = Field(
        default_factory=lambda: ["tiny", "base", "small", "medium", "large", "turbo"]
    )


class LoggingSchema(BaseModel):
    log_level: str = "INFO"
    log_to_file: bool = True
    log_file_path: str = "logs/app.log"

class ConfigSchema(BaseModel):
    # Existing configurations
    LogCleanup: Optional[LogCleanupConfig] = None
    Logging: LoggingConfig = LoggingConfig()
    audio_device_index: Optional[int] = sd.default.device[0]
    channels: int = 1
    documentation_file: str = "README.md"
    dtype: str = "float32"
    enable_noise_reduction: bool = True
    enable_system_monitoring: bool = True
    gui_settings: Optional[GUISettingsConfig] = None
    key_combination: List[str] = Field(default_factory=lambda: ['ctrl', 'alt', 'space'])
    key_listener_sleep: float = 0.1
    max_recording_duration: int = 60
    model_support: ModelSupportSchema = ModelSupportSchema()
    record_audio: bool = True
    samplerate: int = 16000
    save_audio: bool = False
    save_directory: str = "transcriptions"
    save_transcription: bool = False
    use_fp16: bool = True
    noise_reduction_algorithm: Optional[str] = "noisereduce"
    recording_timeout: int = 60  # Default to 60 seconds

    class Config:
        protected_namespaces = ()
