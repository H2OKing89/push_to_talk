# gui/transcription_gui.py

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from utils.gui_utils import create_tooltip
from gui.preferences_window import PreferencesWindow
from gui.help_dialogs import show_user_guide, show_about
from state import state
from utils.logging_utils import sanitize_message
import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend for Tkinter
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from PIL import Image, ImageTk
import os

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
        self.apply_always_on_top()  # Apply the Always on Top setting upon initialization

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
            self.file_menu.add_command(label="Exit", command=self.graceful_shutdown)

            # Help menu
            self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
            self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
            self.help_menu.add_command(label="User Guide", command=lambda: show_user_guide(self.root, self.config))
            self.help_menu.add_command(label="About", command=show_about)

            # Create a frame for the waveform display
            self.top_frame = ttk.Frame(self.root)
            self.top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False, padx=10, pady=10)

            # Setup waveform display
            self.setup_waveform_display()

            # Create a frame for status and progress indicators
            self.status_frame = ttk.Frame(self.root)
            self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

            # Recording indicator circle
            self.indicator_canvas = tk.Canvas(self.status_frame, width=20, height=20, highlightthickness=0)
            self.indicator_canvas.pack(side=tk.LEFT, padx=5)
            self.indicator = self.indicator_canvas.create_oval(5, 5, 15, 15, fill='grey')

            # Status label
            self.status_var = tk.StringVar()
            self.status_var.set("Ready")
            self.status_label = ttk.Label(self.status_frame, textvariable=self.status_var, font=("Helvetica", 12))
            self.status_label.pack(side=tk.LEFT, padx=(0, 10))

            # Progress bar
            self.progress_bar = ttk.Progressbar(self.status_frame, mode='indeterminate')
            self.progress_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))

            # Transcription text box
            self.transcription_text = tk.Text(self.root, wrap=tk.WORD, font=("Helvetica", 12))
            self.transcription_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

            # Exit button
            self.exit_button = ttk.Button(self.root, text="Exit", command=self.graceful_shutdown)
            self.exit_button.pack(side=tk.RIGHT, padx=10, pady=10)

            # Tooltip for exit button
            create_tooltip(self.exit_button, "Exit the application")

            # Status colors mapping
            self.STATUS_COLORS = {
                "Recording": "red",
                "Transcribing": "blue",
                "Idle": "green",
                "Error": "orange",
                "Ready": "black"
            }

        except Exception as e:
            sanitized_error = sanitize_message(str(e))
            logger.error(f"Error setting up GUI: {sanitized_error}", exc_info=True)
            messagebox.showerror("GUI Setup Error", f"Failed to set up the GUI: {e}")

    def setup_waveform_display(self):
        """Sets up the waveform display in the GUI."""
        self.figure = Figure(figsize=(5, 2), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_ylim([-1, 1])  # Adjust based on audio data range
        self.ax.set_xlim(0, 1024)  # Number of samples to display
        self.ax.set_title("Real-Time Audio Waveform")
        self.ax.set_xlabel("Samples")
        self.ax.set_ylabel("Amplitude")
        self.line, = self.ax.plot([], [], lw=1, color='blue')
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.top_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Initialize waveform data
        self.waveform_data = np.zeros(1024)

    def update_waveform(self, audio_chunk):
        """Updates the waveform display with new audio data."""
        try:
            audio_data = audio_chunk.flatten()
            self.waveform_data = np.concatenate((self.waveform_data, audio_data))[-1024:]
            self.line.set_ydata(self.waveform_data)
            self.line.set_xdata(np.arange(len(self.waveform_data)))
            self.ax.draw_artist(self.line)
            self.canvas.draw_idle()
        except Exception as e:
            logger.error(f"Failed to update waveform: {e}", exc_info=True)

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
            self.progress_bar['value'] = 0
        except Exception as e:
            logger.error(f"Failed to stop progress bar: {e}", exc_info=True)

    def update_status(self, status):
        """
        Updates the status label and recording indicator.

        Args:
            status (str): The new status to display.
        """
        try:
            self.status_var.set(status)
            color = self.STATUS_COLORS.get(status, "black")
            self.status_label.config(foreground=color)
            if status == "Recording":
                self.indicator_canvas.itemconfig(self.indicator, fill='red')
            elif status == "Transcribing":
                self.indicator_canvas.itemconfig(self.indicator, fill='blue')
            elif status == "Idle":
                self.indicator_canvas.itemconfig(self.indicator, fill='green')
            elif status == "Error":
                self.indicator_canvas.itemconfig(self.indicator, fill='orange')
            else:
                self.indicator_canvas.itemconfig(self.indicator, fill='grey')
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
            self.update_status("Idle")
        except Exception as e:
            logger.error(f"Failed to set model: {e}", exc_info=True)
            self.update_status("Error")

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
                set_log_level_callback=self.set_log_level_callback,
                apply_always_on_top_callback=self.update_always_on_top  # Pass the callback here
            )
        except Exception as e:
            logger.error(f"Failed to open Preferences window: {e}", exc_info=True)
            messagebox.showerror("Preferences Error", f"Failed to open Preferences window: {e}")

    def apply_always_on_top(self):
        """
        Applies the 'Always on Top' setting to the main window based on the configuration.
        """
        try:
            self.root.attributes('-topmost', self.config.always_on_top)
            logger.info(
                f"'Always on Top' set to {self.config.always_on_top}",
                extra={'correlation_id': self.correlation_id, 'trace_id': self.trace_id}
            )
        except Exception as e:
            logger.error(f"Failed to apply 'Always on Top' setting: {e}", exc_info=True)

    def update_always_on_top(self, new_setting: bool):
        """
        Updates the 'Always on Top' setting dynamically.

        Args:
            new_setting (bool): The new setting for 'Always on Top'.
        """
        try:
            self.root.attributes('-topmost', new_setting)
            self.config.always_on_top = new_setting
            logger.info(
                f"'Always on Top' updated to {new_setting}",
                extra={'correlation_id': self.correlation_id, 'trace_id': self.trace_id}
            )
        except Exception as e:
            logger.error(f"Failed to update 'Always on Top' setting: {e}", exc_info=True)

    def start_timeout_timer(self):
        """
        Starts a timer to automatically stop recording after a timeout.
        """
        try:
            if self.config.max_recording_duration > 0:
                self.timeout_timer = self.root.after(self.config.max_recording_duration * 1000, self.stop_recording_callback)
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

    def graceful_shutdown(self):
        """
        Gracefully shuts down the application.
        """
        try:
            self.graceful_shutdown_callback()
        except Exception as e:
            logger.error(f"Error during graceful shutdown: {e}", exc_info=True)
            messagebox.showerror("Shutdown Error", f"Failed to shut down gracefully: {e}")
