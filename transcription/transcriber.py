import logging
import whisper
import torch
from utils.logging_utils import sanitize_message
from config.schema import ConfigSchema
from utils.helpers import load_model_with_retry
from state import state

logger = logging.getLogger(__name__)

class Transcriber:
    def __init__(self, config: ConfigSchema):
        self.config = config
        self.model = None

    def get_whisper_model(self, model_name):
        """
        Loads the Whisper model based on the provided model name.

        Args:
            model_name (str): The name of the model to load.

        Returns:
            whisper.Model: The loaded Whisper model.
        """
        try:
            logger.info(
                f"Loading Whisper model: {model_name} on device: {self.get_device()}",
                extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id}
            )
            model = whisper.load_model(model_name, device=self.get_device())
            return model
        except TypeError as e:
            sanitized_error = sanitize_message(str(e))
            logger.error(
                f"Failed to load Whisper model '{model_name}': {sanitized_error}",
                extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id},
                exc_info=True
            )
            raise
        except Exception as e:
            sanitized_error = sanitize_message(str(e))
            logger.error(
                f"Unexpected error loading Whisper model '{model_name}': {sanitized_error}",
                extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id},
                exc_info=True
            )
            raise

    def get_device(self):
        """
        Determines the device to load the model on.

        Returns:
            str: The device ('cpu' or 'cuda').
        """
        if torch.cuda.is_available() and self.config.use_gpu:
            return "cuda"
        else:
            return "cpu"

    def load_whisper_model(self, model_name):
        """
        Loads the Whisper model with retry mechanism.

        Args:
            model_name (str): The name of the model to load.

        Returns:
            whisper.Model: The loaded Whisper model.
        """
        try:
            self.model = load_model_with_retry(
                self.get_whisper_model,
                model_name=model_name,
                retries=3,
                delay=2
            )
            
            # **Assign the model's name**
            self.model.name = model_name  # Manually set the model name here
            
            return self.model
        except Exception as e:
            sanitized_error = sanitize_message(str(e))
            logger.error(
                f"Error loading Whisper model '{model_name}': {sanitized_error}",
                extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id},
                exc_info=True
            )
            raise
