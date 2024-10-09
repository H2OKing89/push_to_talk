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
    def __init__(
        self,
        parent,
        config: ConfigSchema,
        correlation_id,
        trace_id,
        on_model_change_callback,
        set_log_level_callback,
        apply_always_on_top_callback=None
    ):
        super().__init__(parent)
        self.title("Preferences")
        self.config = config
        self.correlation_id = correlation_id
        self.trace_id = trace_id
        self.on_model_change_callback = on_model_change_callback
        self.set_log_level_callback = set_log_level_callback
        self.apply_always_on_top_callback = apply_always_on_top_callback  # Store the callback

        # **Make the Preferences window transient and modal**
        self.transient(parent)  # Set to be on top of the main window
        self.grab_set()         # Make the window modal
        self.focus_set()        # Set focus to the Preferences window
        self.attributes('-topmost', True)  # Ensure it's always on top

        # **Center the Preferences window over the main window**
        self.center_window(parent)

        self.create_widgets()

    def center_window(self, parent):
        """Centers the Preferences window over the parent window."""
        self.update_idletasks()  # Ensure window dimensions are calculated

        # Get the parent window's position and size
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        # Get the Preferences window's size
        window_width = self.winfo_width()
        window_height = self.winfo_height()

        # If window size is not yet determined, set a default size
        if window_width <= 1 and window_height <= 1:
            window_width = 400
            window_height = 400  # Increased height to accommodate more settings
            self.geometry(f"{window_width}x{window_height}")

        # Recalculate in case the window was just sized
        self.update_idletasks()

        # Get updated window size
        window_width = self.winfo_width()
        window_height = self.winfo_height()

        # Calculate position to center the window
        position_right = parent_x + (parent_width // 2) - (window_width // 2)
        position_down = parent_y + (parent_height // 2) - (window_height // 2)

        # Set the geometry of the Preferences window
        self.geometry(f"+{position_right}+{position_down}")

    def create_widgets(self):
        try:
            logger.debug(
                f"Available models: {self.config.model_support.available_models}",
                extra={'correlation_id': self.correlation_id, 'trace_id': self.trace_id}
            )
            # Create a main frame to hold all widgets with padding
            main_frame = ttk.Frame(self, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)

            # Configure grid layout with appropriate row and column weights
            for i in range(10):
                main_frame.rowconfigure(i, weight=1)
            main_frame.columnconfigure(0, weight=1)
            main_frame.columnconfigure(1, weight=2)

            # Model selection
            ttk.Label(main_frame, text="Select Model:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            self.model_var = tk.StringVar(value=self.config.model_support.default_model)
            self.model_combo = ttk.Combobox(
                main_frame,
                textvariable=self.model_var,
                values=self.config.model_support.available_models,
                state="readonly"
            )
            self.model_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)

            # Log level selection
            ttk.Label(main_frame, text="Log Level:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
            self.log_level_var = tk.StringVar(value=self.config.Logging.log_level)
            self.log_level_combo = ttk.Combobox(
                main_frame,
                textvariable=self.log_level_var,
                values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                state="readonly"
            )
            self.log_level_combo.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)

            # Audio device selection
            ttk.Label(main_frame, text="Select Audio Device:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
            self.audio_device_var = tk.StringVar()
            input_devices = [device for device in sd.query_devices() if device['max_input_channels'] > 0]
            device_names = [f"{idx}: {device['name']}" for idx, device in enumerate(input_devices)]
            self.audio_device_combo = ttk.Combobox(
                main_frame,
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
            self.audio_device_combo.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)

            # Enable Noise Reduction
            ttk.Label(main_frame, text="Enable Noise Reduction:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
            self.noise_reduction_var = tk.BooleanVar(value=self.config.enable_noise_reduction)
            self.noise_reduction_checkbox = ttk.Checkbutton(main_frame, variable=self.noise_reduction_var)
            self.noise_reduction_checkbox.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

            # Maximum recording duration
            ttk.Label(main_frame, text="Max Recording Duration (seconds):").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
            self.max_duration_var = tk.IntVar(value=self.config.max_recording_duration)
            self.max_duration_spinbox = ttk.Spinbox(
                main_frame,
                from_=10,
                to=600,
                increment=1,
                textvariable=self.max_duration_var
            )
            self.max_duration_spinbox.grid(row=4, column=1, padx=5, pady=5, sticky=tk.EW)

            # Save audio option
            ttk.Label(main_frame, text="Save Audio Recordings:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
            self.save_audio_var = tk.BooleanVar(value=self.config.save_audio)
            self.save_audio_checkbox = ttk.Checkbutton(main_frame, variable=self.save_audio_var)
            self.save_audio_checkbox.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)

            # Save transcription option
            ttk.Label(main_frame, text="Save Transcriptions:").grid(row=6, column=0, sticky=tk.W, padx=5, pady=5)
            self.save_transcription_var = tk.BooleanVar(value=self.config.save_transcription)
            self.save_transcription_checkbox = ttk.Checkbutton(main_frame, variable=self.save_transcription_var)
            self.save_transcription_checkbox.grid(row=6, column=1, padx=5, pady=5, sticky=tk.W)

            # Key combination for recording
            ttk.Label(main_frame, text="Key Combination for Recording:").grid(row=7, column=0, sticky=tk.W, padx=5, pady=5)
            self.key_combination_var = tk.StringVar(value=" + ".join(self.config.key_combination))
            self.key_combination_entry = ttk.Entry(main_frame, textvariable=self.key_combination_var)
            self.key_combination_entry.grid(row=7, column=1, padx=5, pady=5, sticky=tk.EW)

            # Enable system monitoring
            ttk.Label(main_frame, text="Enable System Monitoring:").grid(row=8, column=0, sticky=tk.W, padx=5, pady=5)
            self.system_monitoring_var = tk.BooleanVar(value=self.config.enable_system_monitoring)
            self.system_monitoring_checkbox = ttk.Checkbutton(main_frame, variable=self.system_monitoring_var)
            self.system_monitoring_checkbox.grid(row=8, column=1, padx=5, pady=5, sticky=tk.W)

            # **Checkbox for "Always on Top"**
            ttk.Label(main_frame, text="Always on Top:").grid(row=9, column=0, sticky=tk.W, padx=5, pady=5)
            self.always_on_top_var = tk.BooleanVar(value=self.config.always_on_top)
            self.always_on_top_checkbox = ttk.Checkbutton(main_frame, variable=self.always_on_top_var)
            self.always_on_top_checkbox.grid(row=9, column=1, padx=5, pady=5, sticky=tk.W)

            # Save and Cancel buttons
            self.save_button = ttk.Button(main_frame, text="Save", command=self.save_preferences)
            self.save_button.grid(row=10, column=0, padx=5, pady=15, sticky=tk.E)

            self.cancel_button = ttk.Button(main_frame, text="Cancel", command=self.destroy)
            self.cancel_button.grid(row=10, column=1, padx=5, pady=15, sticky=tk.W)

            # Tooltip for Save button
            create_tooltip(self.save_button, "Save your preferences")

            # Configure padding for all children
            for child in main_frame.winfo_children():
                child.grid_configure(padx=5, pady=5)

        except Exception as e:  # Add an except block to handle any exceptions
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
            if selected_device:
                try:
                    device_index = int(selected_device.split(":")[0])  # Extract the index from "index: name"
                    if device_index != self.config.audio_device_index:
                        self.config.audio_device_index = device_index
                        logger.info(
                            f"Audio device changed to {selected_device}",
                            extra={'correlation_id': self.correlation_id, 'trace_id': self.trace_id}
                        )
                        # Additional callback if needed for audio device changes
                except ValueError:
                    raise ValueError(f"Invalid audio device selection: {selected_device}")
            else:
                logger.warning(
                    "No audio device selected.",
                    extra={'correlation_id': self.correlation_id, 'trace_id': self.trace_id}
                )

            # Update noise reduction
            self.config.enable_noise_reduction = self.noise_reduction_var.get()

            # Update max recording duration
            self.config.max_recording_duration = self.max_duration_var.get()

            # Update save audio and transcription options
            self.config.save_audio = self.save_audio_var.get()
            self.config.save_transcription = self.save_transcription_var.get()

            # Update key combination
            key_combination = self.key_combination_var.get().strip()
            if key_combination:
                self.config.key_combination = [key.strip() for key in key_combination.split("+")]
            else:
                raise ValueError("Key combination cannot be empty.")

            # Update system monitoring
            self.config.enable_system_monitoring = self.system_monitoring_var.get()

            # **Update Always on Top Setting**
            new_always_on_top = self.always_on_top_var.get()
            if new_always_on_top != self.config.always_on_top:
                self.config.always_on_top = new_always_on_top
                logger.info(
                    f"'Always on Top' set to {self.config.always_on_top}",
                    extra={'correlation_id': self.correlation_id, 'trace_id': self.trace_id}
                )
                # **Invoke the callback to update the main window**
                if self.apply_always_on_top_callback:
                    self.apply_always_on_top_callback(self.config.always_on_top)

            # Save the updated configuration
            save_config(self.config)
            logger.info("Preferences saved successfully.", extra={'correlation_id': self.correlation_id, 'trace_id': self.trace_id})
            messagebox.showinfo("Success", "Preferences have been saved successfully.")
            self.destroy()
        except Exception as e:
            sanitized_error = sanitize_message(str(e))
            logger.error(f"Error saving preferences: {sanitized_error}", exc_info=True)
            messagebox.showerror("Error", f"Failed to save preferences: {e}")
