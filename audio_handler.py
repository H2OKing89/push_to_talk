import sounddevice as sd
import numpy as np
import logging
import soundfile as sf
import os
from datetime import datetime
from state import correlation_id

class AudioProcessingError(Exception):
    pass

def start_audio_stream(callback, samplerate, channels, dtype):
    """Starts the audio input stream."""
    try:
        stream = sd.InputStream(
            callback=callback,
            samplerate=samplerate,
            channels=channels,
            dtype=dtype
        )
        stream.start()
        logging.info("Audio input stream started.", extra={'correlation_id': correlation_id})
        return stream
    except Exception as e:
        logging.error(f"Failed to start audio input stream: {e}", extra={'correlation_id': correlation_id}, exc_info=True)
        raise AudioProcessingError(f"Error starting audio stream: {e}")

def save_audio_clip(audio_data, save_dir, samplerate, correlation_id):
    """Saves the recorded audio clip to a file."""
    try:
        timestamp = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
        audio_file = os.path.join(save_dir, f"audio_{timestamp}.wav")
        # Normalize audio to prevent clipping
        audio_normalized = audio_data / np.max(np.abs(audio_data)) if np.max(np.abs(audio_data)) != 0 else audio_data
        os.makedirs(save_dir, exist_ok=True)
        sf.write(audio_file, audio_normalized, samplerate)
        logging.info(f"Audio clip saved to {audio_file}", extra={'correlation_id': correlation_id})
    except Exception as e:
        logging.error(f"Failed to save audio clip: {e}", extra={'correlation_id': correlation_id}, exc_info=True)
        raise AudioProcessingError(f"Error saving audio clip: {e}")
