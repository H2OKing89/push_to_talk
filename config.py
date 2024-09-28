# config.py
import yaml
import os
import logging
from utils import get_absolute_path

class ConfigError(Exception):
    pass

def load_config(config_filename="config.yaml"):
    """Loads the configuration from a YAML file, with defaults for missing entries."""
    try:
        config_path = get_absolute_path(config_filename)
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        config = _apply_defaults(config)
        return config
    except FileNotFoundError:
        logging.error(f"Configuration file not found at: {config_path}")
        raise ConfigError(f"Configuration file missing at: {config_path}")
    except yaml.YAMLError as e:
        logging.error(f"Error parsing the configuration file: {e}")
        raise ConfigError(f"Error parsing configuration: {e}")
    except Exception as e:
        logging.error(f"Failed to load configuration file: {e}")
        raise ConfigError(f"General configuration error: {e}")

def _apply_defaults(config):
    """Applies default values for missing configuration entries."""
    defaults = {
        'Logging': {'log_level': 'INFO', 'log_dir': 'logs/push_to_logs'},
        'AudioBuffer': {'max_duration_seconds': 300},
        'key_combination': ['ctrl', 'alt', 'space'],
        'max_recording_duration': 60,
        'enable_noise_reduction': True  # Added default for noise reduction
    }
    for key, value in defaults.items():
        config.setdefault(key, value)
    return config

def save_config(config, config_filename="config.yaml"):
    """Saves the configuration to a YAML file, with rollback on failure."""
    try:
        config_path = get_absolute_path(config_filename)
        temp_config_path = config_path + ".tmp"
        with open(temp_config_path, 'w') as file:
            yaml.dump(config, file)
        # If successful, replace the original config file
        os.replace(temp_config_path, config_path)
    except Exception as e:
        logging.error(f"Failed to save configuration file: {e}")
        # Remove temporary file if it exists
        if os.path.exists(temp_config_path):
            os.remove(temp_config_path)
        raise ConfigError(f"Error saving configuration: {e}")
