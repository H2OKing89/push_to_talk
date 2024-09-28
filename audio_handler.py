# audio_handler.py

import sounddevice as sd
import logging
from state import correlation_id
from config import ConfigError
from transcription import check_model_availability
import os
from datetime import datetime
import soundfile as sf
from logger import sanitize_message

# Set up module-specific logger
logger = logging.getLogger(__name__)

class AudioProcessingError(Exception):
    """Custom exception for audio processing errors."""
    pass

def start_audio_stream(callback, samplerate, channels, dtype, device=None):
    """Starts the audio input stream."""
    try:
        stream = sd.InputStream(
            callback=callback,
            samplerate=samplerate,
            channels=channels,
            dtype=dtype,
            device=device
        )
        stream.start()
        logger.info("Audio stream started successfully.", extra={'correlation_id': correlation_id})
        return stream
    except Exception as e:
        sanitized_error = sanitize_message(str(e))
        logger.error(
            f"Failed to start audio stream: {sanitized_error}",
            extra={'correlation_id': correlation_id},
            exc_info=True
        )
        raise AudioProcessingError(f"Failed to start audio stream: {e}")

def save_audio_clip(audio_data, save_directory, samplerate, correlation_id):
    """Saves the audio clip to a file."""
    try:
        timestamp = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
        os.makedirs(save_directory, exist_ok=True)
        audio_file = os.path.join(save_directory, f"audio_{timestamp}.wav")
        sf.write(audio_file, audio_data, samplerate)
        logger.info(f"Audio clip saved to {audio_file}", extra={'correlation_id': correlation_id})
    except Exception as e:
        sanitized_error = sanitize_message(str(e))
        logger.error(
            f"Failed to save audio clip: {sanitized_error}",
            extra={'correlation_id': correlation_id},
            exc_info=True
        )
