# gui.py
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import logging
from preferences import PreferencesWindow
from utils import get_absolute_path, create_tooltip
import pyautogui
import numpy as np
from datetime import datetime
import soundfile as sf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Import shared state variables
from state import lock, should_exit, audio_buffer

class TranscriptionGUI:
    def __init__(self, root, config, model, stop_recording_callback, correlation_id, on_model_change_callback):
        self.root = root
        self.config = config
        self.model = model
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
        self.create_widgets()
        self.create_tooltips()
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

    def create_widgets(self):
        """Creates and places all widgets in the GUI."""
        # Status Label
        self.status_label = ttk.Label(self.root, text="Status: Idle", font=("Helvetica", 12))
        self.status_label.pack(pady=5, anchor='w', padx=10)

        # Instructions Label
        keys = ' + '.join([key.upper() for key in self.config.get('key_combination', ['ctrl', 'alt', 'space'])])
        self.instructions_label = ttk.Label(self.root, text=f"Press '{keys}' to toggle recording.", font=("Helvetica", 10))
        self.instructions_label.pack(pady=5, anchor='w', padx=10)

        # Transcription Display
        self.transcription_text = scrolledtext.ScrolledText(self.root, wrap='word', height=10, state='disabled')
        self.transcription_text.pack(pady=10, padx=10, fill='both', expand=True)

        # Waveform Visualization Frame
        self.waveform_frame = ttk.LabelFrame(self.root, text="Live Audio Waveform")
        self.waveform_frame.pack(pady=10, padx=10, fill='both', expand=True)

        # Progress Bar
        self.progress = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=800, mode='indeterminate')
        # Initially hidden; will be shown when needed

        # Exit Button
        self.exit_button = ttk.Button(self.root, text="Exit")
        self.exit_button.pack(pady=5, padx=10, anchor='e')  # Positioned at the bottom-right

    def create_tooltips(self):
        """Creates tooltips for GUI elements."""
        # Example tooltips
        create_tooltip(self.transcription_text, "Transcribed text will appear here.")
        create_tooltip(self.exit_button, "Click to exit the application.")
        # Add more tooltips as needed

    def setup_waveform_plot(self):
        """Sets up the waveform plot using matplotlib."""
        self.fig, self.ax = plt.subplots(figsize=(8, 3))
        self.ax.set_title("Audio Waveform")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Amplitude")
        self.line, = self.ax.plot([], [], lw=1)
        self.ax.set_xlim(0, self.config.get('BUFFER_MAX_DURATION', 120))
        self.ax.set_ylim(-1, 1)
        self.ax.grid(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.waveform_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def open_preferences(self):
        """Opens the preferences window."""
        PreferencesWindow(self.root, self.config, self.apply_preferences)

    def apply_preferences(self):
        """Applies preferences after saving."""
        # Update transcription and audio saving settings
        self.config['save_transcription'] = self.config.get('save_transcription', False)
        self.config['save_audio'] = self.config.get('save_audio', False)

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
        self.progress.pack(pady=5, padx=10, fill='x')

    def stop_progress(self):
        """Stops the progress bar."""
        self.progress.stop()
        self.progress.pack_forget()

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
