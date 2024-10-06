# gui/preferences_window.py

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import sounddevice as sd  # Import sounddevice as sd
from config.schema import ConfigSchema  # Updated import statement
from config.load_save import save_config
from utils.gui_utils import create_tooltip
from utils.logging_utils import sanitize_message
from state import state

logger = logging.getLogger(__name__)

class PreferencesWindow(tk.Toplevel):
    def __init__(self, parent, config: ConfigSchema, correlation_id, trace_id, on_model_change_callback, set_log_level_callback):
        super().__init__(parent)
        self.title("Preferences")
        self.config = config
        self.correlation_id = correlation_id
        self.trace_id = trace_id
        self.on_model_change_callback = on_model_change_callback
        self.set_log_level_callback = set_log_level_callback
        self.create_widgets()

    def create_widgets(self):
        try:
            # Model selection
            ttk.Label(self, text="Select Model:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
            self.model_var = tk.StringVar(value=self.config.model_support.default_model)
            self.model_combo = ttk.Combobox(
                self,
                textvariable=self.model_var,
                values=self.config.model_support.available_models,
                state="readonly"
            )
            self.model_combo.grid(row=0, column=1, padx=10, pady=5)

            # Log level selection
            ttk.Label(self, text="Log Level:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
            self.log_level_var = tk.StringVar(value=self.config.Logging.log_level)
            self.log_level_combo = ttk.Combobox(
                self,
                textvariable=self.log_level_var,
                values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                state="readonly"
            )
            self.log_level_combo.grid(row=1, column=1, padx=10, pady=5)

            # Audio device selection
            ttk.Label(self, text="Select Audio Device:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
            self.audio_device_var = tk.StringVar()
            input_devices = [device for device in sd.query_devices() if device['max_input_channels'] > 0]
            device_names = [f"{idx}: {device['name']}" for idx, device in enumerate(input_devices)]
            self.audio_device_combo = ttk.Combobox(
                self,
                textvariable=self.audio_device_var,
                values=device_names,
                state="readonly"
            )
            # Set the current device based on config.audio_device_index
            current_index = self.config.audio_device_index
            if current_index is not None and 0 <= current_index < len(device_names):
                self.audio_device_var.set(device_names[current_index])
            else:
                # If the configured device index is invalid, select the default device
                default_device = sd.default.device[0]
                if 0 <= default_device < len(device_names):
                    self.audio_device_var.set(device_names[default_device])
                else:
                    self.audio_device_var.set(device_names[0] if device_names else "")
            self.audio_device_combo.grid(row=2, column=1, padx=10, pady=5)

            # Enable Noise Reduction
            ttk.Label(self, text="Enable Noise Reduction:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
            self.noise_reduction_var = tk.BooleanVar(value=self.config.enable_noise_reduction)
            self.noise_reduction_checkbox = ttk.Checkbutton(self, variable=self.noise_reduction_var)
            self.noise_reduction_checkbox.grid(row=3, column=1, padx=10, pady=5)

            # Maximum recording duration
            ttk.Label(self, text="Max Recording Duration (seconds):").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
            self.max_duration_var = tk.IntVar(value=self.config.max_recording_duration)
            self.max_duration_spinbox = ttk.Spinbox(
                self,
                from_=10,
                to=600,
                increment=1,
                textvariable=self.max_duration_var
            )
            self.max_duration_spinbox.grid(row=4, column=1, padx=10, pady=5)

            # Save audio option
            ttk.Label(self, text="Save Audio Recordings:").grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)
            self.save_audio_var = tk.BooleanVar(value=self.config.save_audio)
            self.save_audio_checkbox = ttk.Checkbutton(self, variable=self.save_audio_var)
            self.save_audio_checkbox.grid(row=5, column=1, padx=10, pady=5)

            # Save transcription option
            ttk.Label(self, text="Save Transcriptions:").grid(row=6, column=0, sticky=tk.W, padx=10, pady=5)
            self.save_transcription_var = tk.BooleanVar(value=self.config.save_transcription)
            self.save_transcription_checkbox = ttk.Checkbutton(self, variable=self.save_transcription_var)
            self.save_transcription_checkbox.grid(row=6, column=1, padx=10, pady=5)

            # Key combination for recording
            ttk.Label(self, text="Key Combination for Recording:").grid(row=7, column=0, sticky=tk.W, padx=10, pady=5)
            self.key_combination_var = tk.StringVar(value=" + ".join(self.config.key_combination))
            self.key_combination_entry = ttk.Entry(self, textvariable=self.key_combination_var)
            self.key_combination_entry.grid(row=7, column=1, padx=10, pady=5)

            # Enable system monitoring
            ttk.Label(self, text="Enable System Monitoring:").grid(row=8, column=0, sticky=tk.W, padx=10, pady=5)
            self.system_monitoring_var = tk.BooleanVar(value=self.config.enable_system_monitoring)
            self.system_monitoring_checkbox = ttk.Checkbutton(self, variable=self.system_monitoring_var)
            self.system_monitoring_checkbox.grid(row=8, column=1, padx=10, pady=5)

            # Save and Cancel buttons
            self.save_button = ttk.Button(self, text="Save", command=self.save_preferences)
            self.save_button.grid(row=9, column=0, padx=10, pady=10, sticky=tk.E)

            self.cancel_button = ttk.Button(self, text="Cancel", command=self.destroy)
            self.cancel_button.grid(row=9, column=1, padx=10, pady=10, sticky=tk.W)

            # Tooltip for Save button
            create_tooltip(self.save_button, "Save your preferences")

        except Exception as e:
            sanitized_error = sanitize_message(str(e))
            logger.error(f"Error creating Preferences window widgets: {sanitized_error}", exc_info=True)
            messagebox.showerror("Error", f"Failed to create preferences window: {e}")

    def save_preferences(self):
        try:
            # Save the selected values to the config
            selected_model = self.model_var.get()
            if selected_model != self.config.model_support.default_model:
                self.config.model_support.default_model = selected_model
                logger.info(
                    f"Model changed to {selected_model}",
                    extra={'correlation_id': self.correlation_id, 'trace_id': self.trace_id}
                )
                # Call the model change callback
                if self.on_model_change_callback:
                    self.on_model_change_callback(selected_model)

            # Update log level in config
            selected_log_level = self.log_level_var.get()
            if selected_log_level != self.config.Logging.log_level:
                self.config.Logging.log_level = selected_log_level
                logger.info(
                    f"Log level changed to {selected_log_level}",
                    extra={'correlation_id': self.correlation_id, 'trace_id': self.trace_id}
                )
                # Update the log level in the application
                if self.set_log_level_callback:
                    self.set_log_level_callback(selected_log_level)

            # Update audio device index based on selected device name
            selected_device = self.audio_device_var.get()
            device_index = int(selected_device.split(":")[0])  # Extract the index from "index: name"
            if device_index != self.config.audio_device_index:
                self.config.audio_device_index = device_index
                logger.info(
                    f"Audio device changed to {selected_device}",
                    extra={'correlation_id': self.correlation_id, 'trace_id': self.trace_id}
                )
                # Additional callback if needed for audio device changes

            # Update noise reduction
            self.config.enable_noise_reduction = self.noise_reduction_var.get()

            # Update max recording duration
            self.config.max_recording_duration = self.max_duration_var.get()

            # Update save audio and transcription options
            self.config.save_audio = self.save_audio_var.get()
            self.config.save_transcription = self.save_transcription_var.get()

            # Update key combination
            self.config.key_combination = self.key_combination_var.get().split(" + ")

            # Update system monitoring
            self.config.enable_system_monitoring = self.system_monitoring_var.get()

            # Save the updated configuration
            save_config(self.config)
            logger.info("Preferences saved successfully.", extra={'correlation_id': self.correlation_id, 'trace_id': self.trace_id})
            self.destroy()
        except Exception as e:
            sanitized_error = sanitize_message(str(e))
            logger.error(f"Error saving preferences: {sanitized_error}", exc_info=True)
            messagebox.showerror("Error", f"Failed to save preferences: {e}")
