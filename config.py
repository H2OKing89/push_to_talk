# config.py

import yaml
import os
import logging
from utils import get_absolute_path
from state import correlation_id
from logger import sanitize_message

# Set up module-specific logger
logger = logging.getLogger(__name__)

class ConfigError(Exception):
    """Custom exception for configuration errors."""
    pass

def load_config():
    """Loads and validates the configuration from config.yaml."""
    config_path = get_absolute_path('config.yaml')
    if not os.path.exists(config_path):
        logger.error(
            f"Configuration file not found at {config_path}",
            extra={'correlation_id': correlation_id}
        )
        raise ConfigError(f"Configuration file not found at {config_path}")

    with open(config_path, 'r') as file:
        try:
            config = yaml.safe_load(file)
            logger.info("Configuration loaded successfully.", extra={'correlation_id': correlation_id})
        except yaml.YAMLError as e:
            sanitized_error = sanitize_message(str(e))
            logger.error(
                f"Error parsing configuration file: {sanitized_error}",
                extra={'correlation_id': correlation_id},
                exc_info=True
            )
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
            logger.error(
                f"Missing required configuration field: {field}",
                extra={'correlation_id': correlation_id}
            )
            raise ConfigError(f"Missing required configuration field: {field}")

    # Additional validations can be added here

    return config

def save_config(config):
    """Saves the configuration to config.yaml."""
    config_path = get_absolute_path('config.yaml')
    try:
        with open(config_path, 'w') as file:
            yaml.safe_dump(config, file)
            logger.info("Configuration saved successfully.", extra={'correlation_id': correlation_id})
    except Exception as e:
        sanitized_error = sanitize_message(str(e))
        logger.error(
            f"Failed to save configuration: {sanitized_error}",
            extra={'correlation_id': correlation_id},
            exc_info=True
        )
        raise ConfigError(f"Failed to save configuration: {e}")
