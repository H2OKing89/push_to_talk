# audio/saving.py

import os
from datetime import datetime
import soundfile as sf
import logging
import threading
from logger import sanitize_message
from audio.notifications import notify_user
from audio.error import AudioProcessingError

# Set up module-specific logger
logger = logging.getLogger(__name__)

def save_audio_clip(
    audio_data,
    save_directory: str,
    samplerate: int,
    correlation_id: str,
    gui = None  # Pass the GUI instance for notifications
):
    """
    Saves the audio clip to a file asynchronously.

    Args:
        audio_data: The audio data to save.
        save_directory (str): Directory to save audio files.
        samplerate (int): Sampling rate.
        correlation_id (str): Correlation ID for logging.
        gui: GUI instance for user notifications.
    """
    def save_thread():
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
            # Notify the user about the failure
            if gui:
                notify_user(gui, "Save Audio Error", f"Failed to save audio clip.\nError: {e}", level="error")
    
    threading.Thread(target=save_thread, daemon=True).start()
