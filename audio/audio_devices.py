# audio/audio_devices.py

import sounddevice as sd
import logging
from utils.logging_utils import sanitize_message

logger = logging.getLogger(__name__)

# Rest of the code...


def get_input_devices():
    """Retrieves a list of available audio input devices."""
    try:
        devices = sd.query_devices()
        input_devices = []
        for idx, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                input_devices.append({'name': device['name'], 'index': idx})
        return input_devices
    except Exception as e:
        logger.error(
            f"Failed to retrieve audio devices: {sanitize_message(str(e))}",
            exc_info=True
        )
        return []
