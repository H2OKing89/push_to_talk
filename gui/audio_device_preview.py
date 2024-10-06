# gui/audio_device_preview.py

import sounddevice as sd
import numpy as np
import logging
from tkinter import messagebox
from utils.logging_utils import sanitize_message

logger = logging.getLogger(__name__)

class AudioDevicePreview:
    def __init__(self, device_name, input_devices, correlation_id, trace_id):
        self.device_name = device_name
        self.input_devices = input_devices
        self.correlation_id = correlation_id
        self.trace_id = trace_id

    def preview_audio_device(self):
        try:
            # Find the device index
            device_index = next((device['index'] for device in self.input_devices if device['name'] == self.device_name), None)
            if device_index is None:
                raise ValueError(f"Device '{self.device_name}' not found.")
            # Set the device
            sd.default.device = device_index
            # Generate a sine wave and play it
            frequency = 440  # A4 note
            duration = 1  # 1 second
            samplerate = sd.query_devices(device_index)['default_samplerate']
            sine_wave = self._generate_sine_wave(frequency, duration, samplerate)
            sd.play(sine_wave, samplerate=samplerate)
            sd.wait()
            logger.info(
                f"Previewed audio device '{self.device_name}' successfully.",
                extra={'correlation_id': self.correlation_id, 'trace_id': self.trace_id}
            )
        except Exception as e:
            sanitized_error = sanitize_message(str(e))
            logger.error(
                f"Failed to preview audio device: {sanitized_error}",
                extra={'correlation_id': self.correlation_id, 'trace_id': self.trace_id},
                exc_info=True
            )
            messagebox.showerror("Audio Device Preview Error", f"Failed to preview audio device:\n{e}")

    def _generate_sine_wave(self, frequency, duration, samplerate):
        """Generates a sine wave of a given frequency and duration."""
        t = np.linspace(0, duration, int(samplerate * duration), endpoint=False)
        wave = np.sin(2 * np.pi * frequency * t).astype(np.float32)
        return wave
