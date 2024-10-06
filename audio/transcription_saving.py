# audio/transcription_saving.py

import os
from datetime import datetime
import logging
import threading
from utils.logging_utils import sanitize_message
from audio.notifications import notify_user
from audio.error import AudioProcessingError
from state import state  # Ensure 'state' is imported

# Set up module-specific logger
logger = logging.getLogger(__name__)

def save_transcription(
    transcription_text: str,
    save_directory: str,
    correlation_id: str,
    gui=None  # Pass the GUI instance for notifications
):
    """
    Saves the transcription text to a file asynchronously.

    Args:
        transcription_text (str): The transcribed text to save.
        save_directory (str): Directory to save transcription files.
        correlation_id (str): Correlation ID for logging.
        gui: GUI instance for user notifications.
    """
    def save_thread():
        try:
            timestamp = datetime.now().strftime("%m-%d-%Y_%H%M%S")
            os.makedirs(save_directory, exist_ok=True)
            transcription_file = os.path.join(save_directory, f"transcription_{timestamp}.txt")
            with open(transcription_file, 'w', encoding='utf-8') as f:
                f.write(transcription_text)
            logger.info(f"Transcription saved to {transcription_file}", extra={'correlation_id': state.correlation_id})
        except Exception as e:
            sanitized_error = sanitize_message(str(e))
            logger.error(
                f"Failed to save transcription: {sanitized_error}",
                extra={'correlation_id': state.correlation_id},
                exc_info=True
            )
            # Notify the user about the failure
            if gui:
                notify_user(gui, "Save Transcription Error", f"Failed to save transcription.\nError: {e}", level="error")
    
    threading.Thread(target=save_thread, daemon=True).start()
