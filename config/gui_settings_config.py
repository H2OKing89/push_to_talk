# config/gui_settings_config.py

from pydantic import BaseModel, validator

class GUISettingsConfig(BaseModel):
    always_on_top: bool = True
    theme: str = "Default"

    @validator('theme')
    def validate_theme(cls, v):
        if v not in ['Default', 'Dark', 'Light']:
            raise ValueError("theme must be 'Default', 'Dark', or 'Light'")
        return v
