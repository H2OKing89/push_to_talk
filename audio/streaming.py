# audio/streaming.py

import sounddevice as sd
import logging
from typing import Callable, Optional
from audio.error import AudioProcessingError
from utils.logging_utils import sanitize_message
from audio.notifications import notify_user
from config import load_config

logger = logging.getLogger(__name__)

def start_audio_stream(
    callback: Callable,
    samplerate: int,
    channels: int,
    dtype: str,
    device: Optional[int] = None,
    gui = None  # Pass the GUI instance for notifications
) -> sd.InputStream:
    """
    Starts the audio input stream.

    Args:
        callback (Callable): The callback function to process audio data.
        samplerate (int): Sampling rate.
        channels (int): Number of audio channels.
        dtype (str): Data type of audio data.
        device (Optional[int]): Audio device index.
        gui: GUI instance for user notifications.

    Returns:
        sd.InputStream: The started audio stream.

    Raises:
        AudioProcessingError: If audio stream cannot be started.
    """
    try:
        stream = sd.InputStream(
            callback=callback,
            samplerate=samplerate,
            channels=channels,
            dtype=dtype,
            device=device
        )
        stream.start()
        correlation_id = getattr(gui, 'correlation_id', 'N/A') if gui else 'N/A'
        logger.info(
            "Audio stream started successfully.",
            extra={'correlation_id': correlation_id}
        )
        return stream
    except Exception as e:
        sanitized_error = sanitize_message(str(e))
        correlation_id = getattr(gui, 'correlation_id', 'N/A') if gui else 'N/A'
        logger.error(
            f"Failed to start audio stream on device {device}: {sanitized_error}",
            extra={'correlation_id': correlation_id},
            exc_info=True
        )
        # Attempt to switch to default device if not already trying
        try:
            default_device = sd.default.device[0]
            if device != default_device:
                logger.info(
                    f"Attempting to switch to default audio device: {default_device}",
                    extra={'correlation_id': correlation_id}
                )
                stream = sd.InputStream(
                    callback=callback,
                    samplerate=samplerate,
                    channels=channels,
                    dtype=dtype,
                    device=default_device
                )
                stream.start()
                logger.info(
                    "Switched to default audio device successfully.",
                    extra={'correlation_id': correlation_id}
                )
                if gui:
                    notify_user(
                        gui,
                        "Audio Device Warning",
                        f"Failed to start audio stream on device {device}. Switched to default device.",
                        level="warning"
                    )
                return stream
            else:
                raise AudioProcessingError(f"Failed to start audio stream on default device: {e}")
        except Exception as switch_e:
            sanitized_switch_error = sanitize_message(str(switch_e))
            logger.error(
                f"Failed to switch to default audio device: {sanitized_switch_error}",
                extra={'correlation_id': correlation_id},
                exc_info=True
            )
            if gui:
                notify_user(
                    gui,
                    "Audio Stream Error",
                    f"Failed to start audio stream on device {device} and default device.\nError: {switch_e}",
                    level="error"
                )
            raise AudioProcessingError(
                f"Failed to start audio stream on device {device} and default device: {switch_e}"
            ) from switch_e
