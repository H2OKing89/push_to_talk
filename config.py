# config.py
import yaml
import os
import logging
from utils import get_absolute_path

def load_config(config_filename="config.yaml"):
    """Loads the configuration from a YAML file."""
    try:
        config_path = get_absolute_path(config_filename)
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        logging.error(f"Configuration file not found at: {config_path}")
        raise
    except yaml.YAMLError as e:
        logging.error(f"Error parsing the configuration file: {e}")
        raise
    except Exception as e:
        logging.error(f"Failed to load configuration file: {e}")
        raise

def save_config(config, config_filename="config.yaml"):
    """Saves the configuration to a YAML file."""
    try:
        config_path = get_absolute_path(config_filename)
        with open(config_path, 'w') as file:
            yaml.dump(config, file)
    except Exception as e:
        logging.error(f"Failed to save configuration file: {e}")
        raise
