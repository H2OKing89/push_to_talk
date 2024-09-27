# transcription.py
import whisper
import logging

# Import shared state variables
from state import correlation_id

def load_whisper_model(model_name, correlation_id):
    """Loads the specified Whisper model."""
    try:
        logging.info(f"Loading Whisper model: {model_name}", extra={'correlation_id': correlation_id})
        model = whisper.load_model(model_name)
        logging.info(f"Whisper model '{model_name}' loaded successfully.", extra={'correlation_id': correlation_id})
        return model
    except Exception as e:
        logging.error(f"Failed to load Whisper model '{model_name}': {e}", extra={'correlation_id': correlation_id}, exc_info=True)
        raise
