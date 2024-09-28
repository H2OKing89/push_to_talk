# transcription.py
import whisper
import logging
from state import correlation_id
import torch

def load_whisper_model(model_name, correlation_id):
    """Loads the specified Whisper model onto the GPU if available."""
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logging.info(f"Loading Whisper model: {model_name} on device: {device}", extra={'correlation_id': correlation_id})
        model = whisper.load_model(model_name, device=device)
        logging.info(f"Whisper model '{model_name}' loaded successfully on {device}.", extra={'correlation_id': correlation_id})
        return model
    except Exception as e:
        logging.error(f"Failed to load Whisper model '{model_name}': {e}", extra={'correlation_id': correlation_id}, exc_info=True)
        raise

def check_model_availability(model_name):
    """Checks if the specified model is available."""
    available_models = whisper.available_models()
    return model_name in available_models
