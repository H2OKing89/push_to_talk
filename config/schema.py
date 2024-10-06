# config/schema.py

from pydantic import BaseModel, Field
from typing import List, Optional
import sounddevice as sd

from .logging_config import LoggingConfig
from .log_cleanup_config import LogCleanupConfig
from .gui_settings_config import GUISettingsConfig
from .model_support_config import ModelSupportConfig

class ConfigSchema(BaseModel):
    LogCleanup: LogCleanupConfig = LogCleanupConfig()
    Logging: LoggingConfig = LoggingConfig()
    audio_device_index: Optional[int] = sd.default.device[0]
    channels: int = 1
    documentation_file: str = "README.md"
    dtype: str = "float32"
    enable_noise_reduction: bool = True
    enable_system_monitoring: bool = True
    gui_settings: GUISettingsConfig = GUISettingsConfig()
    key_combination: List[str] = Field(default_factory=lambda: ['ctrl', 'alt', 'space'])
    key_listener_sleep: float = 0.1
    max_recording_duration: int = 60
    model_support: ModelSupportConfig = ModelSupportConfig()
    record_audio: bool = True
    samplerate: int = 16000
    save_audio: bool = False
    save_directory: str = "transcriptions"
    save_transcription: bool = False
    use_fp16: bool = True
    noise_reduction_algorithm: Optional[str] = "noisereduce"
