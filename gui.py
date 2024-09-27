# gui.py
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import logging
from preferences import PreferencesWindow
from utils import get_absolute_path, create_tooltip
from config import load_config  # Added import for load_config
import pyautogui
import numpy as np
from datetime import datetime
import soundfile as sf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Import shared state variables
from state import lock, should_exit, audio_buffer

from transcription import load_whisper_model  # Added import for load_whisper_model

class TranscriptionGUI:
    def __init__(self, root, config, model, stop_recording_callback, correlation_id, on_model_change_callback):
        self.root = root
        self.config = config
        self.model = model
        self.current_model_name = config.get('model_support', {}).get('default_model', 'base')  # Track model name
        self.stop_recording_callback = stop_recording_callback  # Callback to stop recording
        self.correlation_id = correlation_id
        self.on_model_change_callback = on_model_change_callback

        self.root.title("Push-to-Talk Transcription")
        self.root.geometry("800x600")  # Adjusted size to be smaller
        self.root.minsize(700, 500)     # Minimum size for dynamic resizing
        self.root.attributes("-topmost", self.config.get('gui_settings', {}).get('always_on_top', True))

        # Initialize variables
        self.is_recording = False
        self.timeout_timer = None
        self.plot_update_interval = 100  # ms

        # Create GUI components
        self.create_menu()
        self.create_main_frame()
        self.setup_waveform_plot()

        # Start waveform updating
        self.update_waveform()

    def create_menu(self):
        """Creates the application menu."""
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        # Settings Menu
        self.settings_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Settings", menu=self.settings_menu)
        self.settings_menu.add_command(label="Preferences", command=self.open_preferences)

        # Help Menu
        self.help_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="User Guide", command=self.show_user_guide)

    def create_main_frame(self):
        """Creates and places all widgets in the main frame."""
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill='both', expand=True)

        # Status Frame
        status_frame = ttk.Frame(self.main_frame)
        status_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)

        ttk.Label(status_frame, text="Status:", font=("Helvetica", 12)).grid(row=0, column=0, sticky='w')
        self.status_label = ttk.Label(status_frame, text="Idle", font=("Helvetica", 12))
        self.status_label.grid(row=0, column=1, sticky='w', padx=(10, 0))
        create_tooltip(self.status_label, "Current status of the application.")

        # Instructions Frame
        instructions_frame = ttk.Frame(self.main_frame)
        instructions_frame.grid(row=1, column=0, sticky='ew', pady=(0, 10))
        instructions_frame.columnconfigure(1, weight=1)

        keys = ' + '.join([key.upper() for key in self.config.get('key_combination', ['ctrl', 'alt', 'space'])])
        ttk.Label(instructions_frame, text="Instructions:", font=("Helvetica", 10)).grid(row=0, column=0, sticky='w')
        self.instructions_label = ttk.Label(instructions_frame, text=f"Press '{keys}' to toggle recording.", font=("Helvetica", 10))
        self.instructions_label.grid(row=0, column=1, sticky='w', padx=(10, 0))
        create_tooltip(self.instructions_label, "Key combination to start/stop recording.")

        # Transcription Display
        transcription_frame = ttk.LabelFrame(self.main_frame, text="Transcription")
        transcription_frame.grid(row=2, column=0, sticky='nsew', pady=(0, 10))
        transcription_frame.columnconfigure(0, weight=1)
        transcription_frame.rowconfigure(0, weight=1)

        self.transcription_text = scrolledtext.ScrolledText(transcription_frame, wrap='word', state='disabled')
        self.transcription_text.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        create_tooltip(self.transcription_text, "Transcribed text will appear here.")

        # Waveform Visualization Frame
        waveform_frame = ttk.LabelFrame(self.main_frame, text="Live Audio Waveform")
        waveform_frame.grid(row=3, column=0, sticky='nsew', pady=(0, 10))
        waveform_frame.columnconfigure(0, weight=1)
        waveform_frame.rowconfigure(0, weight=1)

        self.waveform_canvas = None  # Placeholder for waveform canvas

        # Progress Bar
        self.progress = ttk.Progressbar(self.main_frame, orient=tk.HORIZONTAL, mode='indeterminate')
        self.progress.grid(row=4, column=0, sticky='ew', pady=(0, 10))

        # Exit Button
        exit_frame = ttk.Frame(self.main_frame)
        exit_frame.grid(row=5, column=0, sticky='e')

        self.exit_button = ttk.Button(exit_frame, text="Exit", command=self.on_exit)
        self.exit_button.pack()
        create_tooltip(self.exit_button, "Click to exit the application.")

        # Configure grid weights
        self.main_frame.rowconfigure(2, weight=1)
        self.main_frame.rowconfigure(3, weight=1)
        self.main_frame.columnconfigure(0, weight=1)

    def create_tooltips(self):
        """Creates tooltips for GUI elements."""
        # Example tooltips are already added in create_main_frame()
        pass

    def setup_waveform_plot(self):
        """Sets up the waveform plot using matplotlib."""
        self.fig, self.ax = plt.subplots(figsize=(8, 3))
        self.ax.set_title("Audio Waveform")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Amplitude")
        self.line, = self.ax.plot([], [], lw=1)
        self.ax.set_xlim(0, self.config.get('max_recording_duration', 60))
        self.ax.set_ylim(-1, 1)
        self.ax.grid(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=3, column=0, sticky='nsew', padx=5, pady=5)
        create_tooltip(self.canvas.get_tk_widget(), "Real-time audio waveform visualization.")

    def open_preferences(self):
        """Opens the preferences window."""
        PreferencesWindow(self.root, self.config, self.apply_preferences)

    def apply_preferences(self):
        """Applies preferences after saving."""
        # Reload the configuration
        try:
            new_config = load_config()
            self.config.update(new_config)
            logging.info("Preferences updated successfully.", extra={'correlation_id': self.correlation_id})
            messagebox.showinfo("Preferences", "Preferences updated successfully.")
        except Exception as e:
            logging.error(f"Failed to reload configuration: {e}", extra={'correlation_id': self.correlation_id}, exc_info=True)
            messagebox.showerror("Error", f"Failed to reload configuration: {e}")

        # Update GUI Settings
        always_on_top = self.config.get('gui_settings', {}).get('always_on_top', True)
        self.root.attributes("-topmost", always_on_top)

        # Update Model Support if needed
        default_model = self.config.get('model_support', {}).get('default_model', 'base')
        if default_model != self.current_model_name:
            try:
                self.model = load_whisper_model(default_model, self.correlation_id)
                self.current_model_name = default_model  # Update the tracked model name
                logging.info(f"Switched to model: {default_model}", extra={'correlation_id': self.correlation_id})
                messagebox.showinfo("Model Change", f"Switched to model: {default_model}")
            except Exception as e:
                logging.error(f"Failed to load model '{default_model}': {e}", extra={'correlation_id': self.correlation_id}, exc_info=True)
                messagebox.showerror("Error", f"Failed to load model '{default_model}': {e}")

        # Update Instructions label with new key combination
        keys = ' + '.join([key.upper() for key in self.config.get('key_combination', ['ctrl', 'alt', 'space'])])
        self.instructions_label.config(text=f"Press '{keys}' to toggle recording.")

        # Update waveform x-axis limit
        self.ax.set_xlim(0, self.config.get('max_recording_duration', 60))
        self.canvas.draw()

    def show_user_guide(self):
        """Displays the user guide."""
        try:
            with open(get_absolute_path(self.config.get('documentation_file', 'README.md')), 'r') as file:
                content = file.read()
        except FileNotFoundError:
            content = "User guide not found."

        guide_window = tk.Toplevel(self.root)
        guide_window.title("User Guide")
        guide_window.geometry("800x600")
        guide_window.resizable(True, True)

        guide_text = scrolledtext.ScrolledText(guide_window, wrap='word', state='normal')
        guide_text.pack(expand=True, fill='both')
        guide_text.insert(tk.END, content)
        guide_text.config(state='disabled')

    def update_status(self, status):
        """Updates the status label."""
        self.status_label.config(text=f"Status: {status}")
        self.root.update_idletasks()

    def append_transcription(self, text):
        """Appends transcribed text to the display."""
        self.transcription_text.config(state='normal')
        self.transcription_text.insert(tk.END, text + '\n')
        self.transcription_text.config(state='disabled')
        length = len(self.transcription_text.get("1.0", tk.END).strip())
        self.update_status(f"Transcription length: {length} characters")

    def notify_user(self, message):
        """Displays a pop-up notification to the user."""
        messagebox.showinfo("Notification", message)

    def start_progress(self):
        """Starts the progress bar."""
        self.progress.start()
        self.progress.grid()

    def stop_progress(self):
        """Stops the progress bar."""
        self.progress.stop()
        self.progress.grid_remove()

    def on_exit(self):
        """Handles graceful shutdown."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            logging.info("Application closed by user.", extra={'correlation_id': self.correlation_id})
            global should_exit  # Declare as global to modify the global variable
            should_exit = True
            self.root.quit()

    def start_timeout_timer(self):
        """Starts a timer that will stop recording after a set duration."""
        max_duration = self.config.get('max_recording_duration', 60)  # Default to 60 seconds
        self.timeout_timer = self.root.after(int(max_duration * 1000), self.stop_recording_timeout)

    def stop_timeout_timer(self):
        """Cancels the timeout timer if recording is stopped manually."""
        if self.timeout_timer is not None:
            self.root.after_cancel(self.timeout_timer)
            self.timeout_timer = None

    def stop_recording_timeout(self):
        """Callback function to stop recording when the timer expires."""
        if self.is_recording:
            logging.info("Max recording duration reached. Stopping recording.", extra={'correlation_id': self.correlation_id})
            self.update_status("Idle")
            self.stop_recording_callback()  # Invoke the callback to stop recording
            self.stop_timeout_timer()

    def update_waveform(self):
        """Updates the waveform plot with the latest audio data."""
        if self.is_recording:
            with lock:
                if audio_buffer:
                    current_buffer = np.concatenate(audio_buffer).flatten()
                    # Prevent division by zero
                    max_abs = np.max(np.abs(current_buffer))
                    if max_abs != 0:
                        current_buffer = current_buffer / max_abs
                    samplerate = self.config.get('samplerate', 16000)
                    times = np.linspace(0, len(current_buffer)/samplerate, num=len(current_buffer))
                    self.line.set_data(times, current_buffer)
                    self.ax.set_xlim(0, max(10, times[-1]))
                    self.ax.set_ylim(-1, 1)
                    self.canvas.draw()

        # Schedule the next update
        if not should_exit:
            self.root.after(self.plot_update_interval, self.update_waveform)
