# config.py
import yaml
import os
from utils import get_absolute_path
from state import correlation_id

class ConfigError(Exception):
    """Custom exception for configuration errors."""
    pass

def load_config():
    """Loads and validates the configuration from config.yaml."""
    config_path = get_absolute_path('config.yaml')
    if not os.path.exists(config_path):
        raise ConfigError(f"Configuration file not found at {config_path}")
    
    with open(config_path, 'r') as file:
        try:
            config = yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise ConfigError(f"Error parsing configuration file: {e}")
    
    # Perform validation checks
    required_fields = [
        'model_support',
        'key_combination',
        'samplerate',
        'channels',
        'dtype',
        'gui_settings',
        'Logging',
        'enable_noise_reduction',
        'max_recording_duration',
        'LogCleanup'
    ]
    
    for field in required_fields:
        if field not in config:
            raise ConfigError(f"Missing required configuration field: {field}")
    
    # Additional validations can be added here
    
    return config

def save_config(config):
    """Saves the configuration to config.yaml."""
    config_path = get_absolute_path('config.yaml')
    with open(config_path, 'w') as file:
        yaml.safe_dump(config, file)
