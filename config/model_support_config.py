# config/model_support_config.py

from pydantic import BaseModel, Field, validator
from typing import List

class ModelSupportConfig(BaseModel):
    available_models: List[str] = Field(default_factory=lambda: ['tiny', 'base', 'small', 'medium', 'large'])
    default_model: str = "base"

    @validator('default_model')
    def validate_default_model(cls, v, values):
        if 'available_models' in values and v not in values['available_models']:
            raise ValueError(f"default_model must be one of {values['available_models']}")
        return v
