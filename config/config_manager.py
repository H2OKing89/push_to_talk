# config/config_manager.py

import logging
from config.load_save import save_config
from config.exceptions import ConfigError

logger = logging.getLogger(__name__)

class ConfigManager:
    def __init__(self, config):
        self.config = config

    def update_preferences(
        self,
        model_var,
        noise_reduction_var,
        key_combination,
        key_listener_sleep,
        always_on_top,
        gui_theme,
        log_level,
        log_to_console,
        device_name,
        input_devices
    ):
        # Update the config object with new preferences
        self.config.model_support.default_model = model_var
        self.config.enable_noise_reduction = noise_reduction_var
        self.config.key_combination = key_combination
        self.config.key_listener_sleep = key_listener_sleep
        self.config.gui_settings.always_on_top = always_on_top
        self.config.gui_settings.theme = gui_theme
        self.config.Logging.log_level = log_level
        self.config.Logging.log_to_console = log_to_console
        
        # Update audio device index based on selected device name
        selected_device = next((device for device in input_devices if device['name'] == device_name), None)
        if selected_device:
            self.config.audio_device_index = selected_device['index']
        else:
            raise ConfigError(f"Selected audio device '{device_name}' not found.")
        
        # Save the updated configuration
        try:
            save_config(self.config)
            logger.info("Preferences saved successfully.")
        except ConfigError as e:
            logger.error(f"Failed to save preferences: {str(e)}", exc_info=True)
            raise e
