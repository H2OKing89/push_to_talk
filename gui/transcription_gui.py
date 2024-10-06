# gui/transcription_gui.py

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from utils.gui_utils import create_tooltip
from gui.preferences_window import PreferencesWindow
from gui.help_dialogs import show_user_guide, show_about
from state import state
from utils.logging_utils import sanitize_message

# Set up module-specific logger
logger = logging.getLogger(__name__)

class TranscriptionGUI:
    def __init__(
        self,
        root,
        config,
        model,
        stop_recording_callback,
        correlation_id,
        trace_id,
        on_model_change_callback,
        graceful_shutdown_callback,
        set_log_level_callback
    ):
        self.root = root
        self.config = config
        self.model = model
        self.stop_recording_callback = stop_recording_callback
        self.correlation_id = correlation_id
        self.trace_id = trace_id
        self.on_model_change_callback = on_model_change_callback
        self.graceful_shutdown_callback = graceful_shutdown_callback
        self.set_log_level_callback = set_log_level_callback

        self.is_recording = False
        self.timeout_timer = None

        self.setup_gui()

    def setup_gui(self):
        try:
            self.root.title("Transcription App")
            self.root.geometry("800x600")

            # Create menu bar
            self.menu_bar = tk.Menu(self.root)
            self.root.config(menu=self.menu_bar)

            # File menu
            self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
            self.menu_bar.add_cascade(label="File", menu=self.file_menu)
            self.file_menu.add_command(label="Preferences", command=self.open_preferences)
            self.file_menu.add_separator()
            self.file_menu.add_command(label="Exit", command=self.graceful_shutdown_callback)

            # Help menu
            self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
            self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
            self.help_menu.add_command(label="User Guide", command=show_user_guide)
            self.help_menu.add_command(label="About", command=show_about)

            # Status label
            self.status_var = tk.StringVar()
            self.status_var.set("Initializing...")
            self.status_label = ttk.Label(self.root, textvariable=self.status_var)
            self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

            # Progress bar
            self.progress_var = tk.IntVar()
            self.progress_bar = ttk.Progressbar(self.root, variable=self.progress_var, mode='indeterminate')
            self.progress_bar.pack(side=tk.BOTTOM, fill=tk.X)

            # Transcription text box
            self.transcription_text = tk.Text(self.root, wrap=tk.WORD)
            self.transcription_text.pack(expand=True, fill=tk.BOTH)

            # Exit button
            self.exit_button = ttk.Button(self.root, text="Exit", command=self.graceful_shutdown_callback)
            self.exit_button.pack(side=tk.RIGHT, padx=10, pady=10)

            # Tooltip for exit button
            create_tooltip(self.exit_button, "Exit the application")

        except Exception as e:
            sanitized_error = sanitize_message(str(e))
            logger.error(f"Error setting up GUI: {sanitized_error}", exc_info=True)

    def start_progress(self):
        """
        Starts the progress bar.
        """
        try:
            self.progress_bar.start()
        except Exception as e:
            logger.error(f"Failed to start progress bar: {e}", exc_info=True)

    def stop_progress(self):
        """
        Stops the progress bar.
        """
        try:
            self.progress_bar.stop()
            self.progress_var.set(0)
        except Exception as e:
            logger.error(f"Failed to stop progress bar: {e}", exc_info=True)

    def update_status(self, status):
        """
        Updates the status label in the GUI.

        Args:
            status (str): The new status to display.
        """
        try:
            self.status_var.set(status)
        except Exception as e:
            logger.error(f"Failed to update status: {e}", exc_info=True)

    def append_transcription(self, text):
        """
        Appends transcribed text to the transcription text box.

        Args:
            text (str): The transcribed text.
        """
        try:
            self.transcription_text.insert(tk.END, text + '\n')
            self.transcription_text.see(tk.END)
        except Exception as e:
            logger.error(f"Failed to append transcription: {e}", exc_info=True)

    def set_model(self, model):
        """
        Sets the transcription model.

        Args:
            model: The transcription model to set.
        """
        try:
            self.model = model
            logger.info(f"Transcription model set to {model}.", extra={'correlation_id': self.correlation_id, 'trace_id': self.trace_id})
        except Exception as e:
            logger.error(f"Failed to set model: {e}", exc_info=True)

    def open_preferences(self):
        """
        Opens the Preferences window.
        """
        try:
            PreferencesWindow(
                parent=self.root,
                config=self.config,
                correlation_id=self.correlation_id,
                trace_id=self.trace_id,
                on_model_change_callback=self.on_model_change_callback,
                set_log_level_callback=self.set_log_level_callback
            )
        except Exception as e:
            logger.error(f"Failed to open Preferences window: {e}", exc_info=True)

    def start_timeout_timer(self):
        """
        Starts a timer to automatically stop recording after a timeout.
        """
        try:
            if self.config.recording_timeout > 0:
                self.timeout_timer = self.root.after(self.config.recording_timeout * 1000, self.stop_recording_callback)
        except Exception as e:
            logger.error(f"Failed to start timeout timer: {e}", exc_info=True)

    def stop_timeout_timer(self):
        """
        Stops the recording timeout timer.
        """
        try:
            if self.timeout_timer is not None:
                self.root.after_cancel(self.timeout_timer)
                self.timeout_timer = None
        except Exception as e:
            logger.error(f"Failed to stop timeout timer: {e}", exc_info=True)
