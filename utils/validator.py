# config/validator.py

from cerberus import Validator
from config.exceptions import ConfigError
from utils.logging_utils import sanitize_message

def validate_config_schema(config):
    """Validates the configuration schema using Cerberus."""
    schema = {
        # Your schema definition here
    }

    v = Validator(schema)
    if not v.validate(config):
        errors = v.errors
        error_messages = "\n".join([f"{field}: {', '.join(err)}" for field, err in errors.items()])
        raise ConfigError(f"Configuration validation failed:\n{error_messages}")
