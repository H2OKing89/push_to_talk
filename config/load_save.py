# config/load_save.py

import yaml
import os
import logging
from pydantic import ValidationError
from .schema import ConfigSchema
from .exceptions import ConfigError
from utils.file_utils import get_absolute_path
from state import state
from utils.logging_utils import sanitize_message

logger = logging.getLogger(__name__)

def load_config() -> ConfigSchema:
    """Loads and validates the configuration from config.yaml."""
    config_path = get_absolute_path('config.yaml')
    if not os.path.exists(config_path):
        logger.warning(
            f"Configuration file not found at {config_path}. Generating default configuration.",
            extra={'correlation_id': state.correlation_id}
        )
        default_config = ConfigSchema()
        save_config(default_config)
        logger.info(
            f"Default configuration generated at {config_path}.",
            extra={'correlation_id': state.correlation_id}
        )
        return default_config

    with open(config_path, 'r') as file:
        try:
            config_data = yaml.safe_load(file) or {}
            config = ConfigSchema(**config_data)
            logger.info(
                "Configuration loaded and validated successfully.",
                extra={'correlation_id': state.correlation_id}
            )
        except ValidationError as ve:
            sanitized_error = sanitize_message(str(ve))
            logger.error(
                f"Configuration validation error: {sanitized_error}",
                extra={'correlation_id': state.correlation_id},
                exc_info=True
            )
            raise ConfigError(f"Configuration validation error: {ve}") from ve
        except yaml.YAMLError as e:
            sanitized_error = sanitize_message(str(e))
            logger.error(
                f"Error parsing configuration file: {sanitized_error}",
                extra={'correlation_id': state.correlation_id},
                exc_info=True
            )
            raise ConfigError(f"Error parsing configuration file: {e}") from e

    return config

def save_config(config: ConfigSchema) -> None:
    """Saves the configuration to config.yaml."""
    config_path = get_absolute_path('config.yaml')
    try:
        with open(config_path, 'w') as file:
            yaml.safe_dump(config.dict(), file)
            logger.info(
                "Configuration saved successfully.",
                extra={'correlation_id': state.correlation_id}
            )
    except Exception as e:
        sanitized_error = sanitize_message(str(e))
        logger.error(
            f"Failed to save configuration: {sanitized_error}",
            extra={'correlation_id': state.correlation_id},
            exc_info=True
        )
        raise ConfigError(f"Failed to save configuration: {e}") from e
