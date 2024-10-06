# transcription/transcriber.py

import whisper
import logging
import torch
from functools import lru_cache
from state.state_manager import state
from utils.logging_utils import sanitize_message

# Set up module-specific logger
logger = logging.getLogger(__name__)

class Transcriber:
    def __init__(self):
        pass

    @lru_cache(maxsize=None)
    def get_whisper_model(self, model_name: str):
        """Caches Whisper models to reduce load times."""
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(
                f"Loading Whisper model: {model_name} on device: {device}",
                extra={'correlation_id': state.correlation_id}
            )
            model = whisper.load_model(model_name, device=device)
            logger.info(
                f"Whisper model '{model_name}' loaded successfully on {device}.",
                extra={'correlation_id': state.correlation_id}
            )
            return model
        except Exception as e:
            sanitized_error = sanitize_message(str(e))
            logger.error(
                f"Failed to load Whisper model '{model_name}': {sanitized_error}",
                extra={'correlation_id': state.correlation_id},
                exc_info=True
            )
            raise

    def load_whisper_model(self, model_name: str):
        """Loads the specified Whisper model."""
        try:
            model = self.get_whisper_model(model_name)
            return model
        except Exception as e:
            logger.error(
                f"Error loading Whisper model '{model_name}': {sanitize_message(str(e))}",
                extra={'correlation_id': state.correlation_id},
                exc_info=True
            )
            raise

    def check_model_availability(self, model_name: str) -> bool:
        """Checks if the specified model is available."""
        available_models = whisper.available_models()
        return model_name in available_models
