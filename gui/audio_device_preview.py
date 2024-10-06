# gui/audio_device_preview.py

import sounddevice as sd
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
            selected_device = next((device for device in self.input_devices if device['name'] == self.device_name), None)
            if selected_device:
                sd.default.device = (selected_device['index'], sd.default.device[1])
                sd.play(self._generate_sine_wave(440, duration=1), samplerate=sd.default.samplerate)
                sd.wait()
                messagebox.showinfo("Preview", f"Audio device '{self.device_name}' is working properly.")
            else:
                messagebox.showerror("Preview Error", "Selected audio device not found.")
        except Exception as e:
            sanitized_error = sanitize_message(str(e))
            logger.error(
                f"Failed to preview audio device: {sanitized_error}",
                extra={'correlation_id': self.correlation_id, 'trace_id': self.trace_id},
                exc_info=True
            )
            messagebox.showerror("Preview Error", f"Failed to preview audio device: {e}")

    def _generate_sine_wave(self, frequency, duration):
        # Implement sine wave generation logic
        pass
