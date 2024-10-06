# config/config_manager.py

import logging  # Add this import statement
from config.load_save import save_config
from config.exceptions import ConfigError

logger = logging.getLogger(__name__)

class ConfigManager:
    def __init__(self, config):
        self.config = config

    def update_preferences(self, **kwargs):
        # Extract variables from kwargs
        # Update the config dictionary accordingly

        # Example:
        selected_model = kwargs.get('model_var').get()
        self.config['model_support']['default_model'] = selected_model

        # Continue updating other config values

        try:
            save_config(self.config)
            logger.info("Preferences saved successfully.")
        except ConfigError as e:
            logger.error(f"Failed to save preferences: {str(e)}", exc_info=True)
            raise e
