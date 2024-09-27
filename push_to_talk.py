import sounddevice as sd
import numpy as np
import whisper
import keyboard
import pyautogui
import time
import threading
import os
import yaml
import logging
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import uuid
import psutil
import winsound
import sys

# -----------------------------------------------------------------------------
# Push-to-Talk Transcription Application
# Version: 1.2.4
# Author: Quentin
# Released: September 2024
# -----------------------------------------------------------------------------
#
# Version History:
# -----------------------------------------------------------------------------
# Version 1.2.4 (September 2024):
# - Fixed incorrect usage of the 'weights_only' parameter in 'whisper.load_model'.
# - Enhanced error logging in 'load_whisper_model' to capture full exception details.
# - Updated version information as a bug fix release.
#
# Version 1.2.3 (September 2024):
# - Fixed tooltip bindings to correctly attach to widgets instead of BooleanVar instances.
# - Introduced 'save_audio' toggle to enable or disable saving audio clips locally.
# - Updated version information as a bug fix release.
#
# Version 1.2.2 (September 2024):
# - Implemented various improvements for performance, error handling, and UI enhancements.
# - Added configuration toggles for audio recording and transcription saving.
#
# Version 1.2.1 (September 2024):
# - Added recording timeout functionality to automatically stop recording after a set duration.
# - Enhanced logging for timeout events.
#
# Version 1.2.0 (September 2024):
# - Disabled saving of transcription and audio files.
#
# Version 1.0.0 (September 2024):
# - Initial release with basic transcription using Whisper models.
# - Configurable via a YAML file for key combinations, model selection, and GUI settings.
# - Integrated keyboard-based push-to-talk functionality using a customizable key combination.
# - Developed a simple Tkinter-based GUI to display transcriptions and provide model selection.
# - Basic system monitoring included for memory and CPU usage during transcription.
# - Audio is recorded via `sounddevice`, transcribed using the Whisper model, and optionally saved as a WAV file.
# - Added JSON structured logging with log rotation and cleanup based on time or size.
# - Enabled error handling and logging of unexpected issues.
# - Basic tooltip support for guiding the user through the GUI.
# - Added progress bar during transcription and audio recording process.
# - Optional soundfile support for saving audio.
#
# Known Issues:
# - GUI layout is fixed, with no support for dynamic resizing or advanced themes.
# - Splice functionality for editing the transcription is not implemented.
# - No waveform visualization for the audio being recorded.
#
# Upcoming Features:
# - Splice functionality to allow cutting and merging audio segments.
# - Implementation of undo/redo for splicing actions.
# - Waveform visualization to help navigate recorded audio.
# -----------------------------------------------------------------------------

# --------------------- Configuration ---------------------

def get_absolute_path(relative_path):
    """Returns the absolute path based on the script's location."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, relative_path)

# Generate a unique correlation ID for this session
correlation_id = str(uuid.uuid4())

def setup_logging(config):
    """Sets up structured JSON logging with log rotation and cleanup."""
    logger = logging.getLogger()
    log_level = getattr(logging, config['Logging'].get('log_level', 'INFO').upper(), logging.INFO)
    logger.setLevel(log_level)

    # Create log directory if it doesn't exist
    log_dir = get_absolute_path(config['Logging'].get('log_dir', 'logs/push_to_logs'))
    os.makedirs(log_dir, exist_ok=True)

    # Log file path
    log_file = os.path.join(log_dir, 'push_to_talk.log')

    # Create log formatter with 'asctime' and 'levelname'
    log_formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s %(lineno)s %(funcName)s',
        rename_fields={
            'asctime': 'timestamp',
            'levelname': 'level',
            'name': 'logger',
            'message': 'message',
            'lineno': 'line_no',
            'funcName': 'function'
        }
    )

    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=config['LogCleanup'].get('max_log_files', 10)
    )
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)

    # Console handler
    if config['Logging'].get('log_to_console', True):
        console_log_level = getattr(logging, config['Logging'].get('console_log_level', 'INFO').upper(), logging.INFO)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_log_level)
        console_handler.setFormatter(log_formatter)
        logger.addHandler(console_handler)

    # Implement log cleanup
    if config['LogCleanup'].get('cleanup_enabled', True):
        retention_strategy = config['LogCleanup'].get('retention_strategy', 'time')
        retention_days = config['LogCleanup'].get('retention_days', 7)
        if retention_strategy == 'time':
            cleanup_logs_by_time(log_dir, retention_days)
        elif retention_strategy == 'size':
            cleanup_logs_by_size(log_dir, config['LogCleanup'].get('max_log_files', 10))

def cleanup_logs_by_time(log_dir, retention_days):
    """Deletes log files older than the retention period."""
    now = time.time()
    for filename in os.listdir(log_dir):
        file_path = os.path.join(log_dir, filename)
        if os.path.isfile(file_path):
            file_mtime = os.path.getmtime(file_path)
            if (now - file_mtime) > (retention_days * 86400):  # 86400 seconds in a day
                try:
                    os.remove(file_path)
                    logging.info(f"Deleted old log file: {file_path}", extra={'correlation_id': correlation_id})
                except Exception as e:
                    logging.error(f"Failed to delete log file {file_path}: {e}", extra={'correlation_id': correlation_id})

def cleanup_logs_by_size(log_dir, max_log_files):
    """Keeps only the most recent 'max_log_files' log files."""
    try:
        log_files = sorted(
            [os.path.join(log_dir, f) for f in os.listdir(log_dir) if os.path.isfile(os.path.join(log_dir, f))],
            key=lambda x: os.path.getmtime(x),
            reverse=True
        )
        for log_file in log_files[max_log_files:]:
            os.remove(log_file)
            logging.info(f"Deleted excess log file: {log_file}", extra={'correlation_id': correlation_id})
    except Exception as e:
        logging.error(f"Error during log cleanup by size: {e}", extra={'correlation_id': correlation_id})

def load_config(config_filename="config.yml"):
    """Loads the configuration from a YAML file."""
    try:
        config_path = get_absolute_path(config_filename)
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            # Initialize logging here to capture config loading logs
            setup_logging(config)
            logging.info(f"Configuration file loaded from: {config_path}", extra={'correlation_id': correlation_id})
        return config
    except FileNotFoundError:
        print(f"Configuration file not found at: {config_path}")
        messagebox.showerror("Configuration Error", f"Configuration file not found at: {config_path}")
        exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing the configuration file: {e}")
        messagebox.showerror("Configuration Error", f"Error parsing the configuration file: {e}")
        exit(1)
    except Exception as e:
        print(f"Failed to load configuration file: {e}")
        messagebox.showerror("Configuration Error", f"Failed to load configuration file: {e}")
        exit(1)

# Load configuration
config = load_config()

# Extract configurations
KEY_COMBINATION = config.get('key_combination', ['ctrl', 'alt', 'space'])
SAVE_DIR = get_absolute_path(config.get('save_directory', 'transcriptions'))
MODEL_NAME = config.get('model_support', {}).get('default_model', 'base')
AVAILABLE_MODELS = config.get('model_support', {}).get('available_models', ['tiny', 'base', 'small', 'medium', 'large'])
SAMPLERATE = config.get('samplerate', 16000)
CHANNELS = config.get('channels', 1)
DTYPE = config.get('dtype', 'float32')
LOG_LEVEL = config.get('Logging', {}).get('log_level', 'INFO').upper()
ALWAYS_ON_TOP = config.get('gui_settings', {}).get('always_on_top', True)
KEY_LISTENER_SLEEP = config.get('key_listener_sleep', 0.1)
ENABLE_SYSTEM_MONITORING = config.get('enable_system_monitoring', True)
SYSTEM_MONITORING_INTERVAL = config.get('system_monitoring_interval', 60)
USE_FP16 = config.get('use_fp16', False)
PROGRESS_BAR_ENABLED = config.get('progress_bar_enabled', True)
DOCUMENTATION_FILE = get_absolute_path(config.get('documentation_file', 'README.md'))
KEY_COMBINATION_CONFIGURABLE = config.get('key_combination_config', {}).get('configurable_via_gui', True)
RECORDING_TIMEOUT = config.get('recording_timeout', 60)  # seconds
BUFFER_MAX_DURATION = config.get('BUFFER_MAX_DURATION', 120)  # seconds
RECORD_AUDIO = config.get('record_audio', True)
SAVE_TRANSCRIPTION = config.get('save_transcription', False)
SAVE_AUDIO = config.get('save_audio', False)  # New parameter

# Ensure the save directory exists
os.makedirs(SAVE_DIR, exist_ok=True)

# --------------------- Error Handling ---------------------

def handle_unexpected_error(type, value, traceback_obj):
    """Handles unexpected errors by logging them."""
    logging.critical(f"Unexpected error: {value}", exc_info=(type, value, traceback_obj), extra={'correlation_id': correlation_id})
    messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {value}")

# Hook into the system's exception handler
sys.excepthook = handle_unexpected_error

# --------------------- GUI Setup ---------------------

class TranscriptionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Push-to-Talk Transcription")
        self.root.geometry("700x700")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", ALWAYS_ON_TOP)

        # Menu
        self.menu = tk.Menu(root)
        root.config(menu=self.menu)
        self.help_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="User Guide", command=self.show_user_guide)

        # Status Label
        self.status_label = ttk.Label(root, text="Status: Idle", font=("Helvetica", 16))
        self.status_label.pack(pady=10)

        # Instructions Frame
        self.instructions_frame = ttk.Frame(root)
        self.instructions_frame.pack(pady=5)

        keys = ' + '.join([key.upper() for key in KEY_COMBINATION])
        self.instructions_label = ttk.Label(self.instructions_frame, text=f"Press '{keys}' to toggle recording.", font=("Helvetica", 12))
        self.instructions_label.pack()

        # Transcription Display
        self.transcription_text = scrolledtext.ScrolledText(root, wrap='word', height=15, width=80, state='disabled')
        self.transcription_text.pack(pady=10)

        # Progress Bar
        if PROGRESS_BAR_ENABLED:
            self.progress = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=600, mode='indeterminate')
            self.progress.pack(pady=5)

        # Model Selection
        self.model_frame = ttk.Frame(root)
        self.model_frame.pack(pady=5)
        self.model_label = ttk.Label(self.model_frame, text="Select Whisper Model:", font=("Helvetica", 12))
        self.model_label.pack(side=tk.LEFT, padx=5)
        self.model_var = tk.StringVar(value=MODEL_NAME)
        self.model_combobox = ttk.Combobox(self.model_frame, textvariable=self.model_var, values=AVAILABLE_MODELS, state='readonly')
        self.model_combobox.pack(side=tk.LEFT, padx=5)
        self.model_combobox.bind("<<ComboboxSelected>>", self.change_model)

        # Key Combination Configuration
        if KEY_COMBINATION_CONFIGURABLE:
            self.key_combo_frame = ttk.LabelFrame(root, text="Configure Key Combination")
            self.key_combo_frame.pack(pady=10, padx=10, fill="x")

            self.available_keys = ['ctrl', 'alt', 'shift', 'space', 'cmd']  # Extend as needed
            self.key_vars = {key: tk.BooleanVar(value=(key in KEY_COMBINATION)) for key in self.available_keys}

            self.key_checkbuttons = []  # To keep references to Checkbutton widgets
            for key in self.available_keys:
                cb = ttk.Checkbutton(self.key_combo_frame, text=key.upper(), variable=self.key_vars[key])
                cb.pack(side=tk.LEFT, padx=5)
                self.key_checkbuttons.append(cb)

            self.save_keys_button = ttk.Button(self.key_combo_frame, text="Save Keys", command=self.save_key_combination)
            self.save_keys_button.pack(side=tk.LEFT, padx=5)

        # Toggles for Transcription Saving and Audio Saving
        self.toggle_frame = ttk.LabelFrame(root, text="Settings")
        self.toggle_frame.pack(pady=10, padx=10, fill="x")

        self.save_transcription_var = tk.BooleanVar(value=SAVE_TRANSCRIPTION)
        self.save_audio_var = tk.BooleanVar(value=SAVE_AUDIO)

        self.save_transcription_cb = ttk.Checkbutton(
            self.toggle_frame,
            text="Enable Transcription Saving",
            variable=self.save_transcription_var,
            command=self.toggle_save_transcription
        )
        self.save_transcription_cb.pack(side=tk.LEFT, padx=10)

        self.save_audio_cb = ttk.Checkbutton(
            self.toggle_frame,
            text="Enable Audio Saving",
            variable=self.save_audio_var,
            command=self.toggle_save_audio
        )
        self.save_audio_cb.pack(side=tk.LEFT, padx=10)

        # Exit Button
        self.exit_button = ttk.Button(root, text="Exit", command=self.on_exit)
        self.exit_button.pack(pady=10)

        # Recording state
        self.is_recording = False
        self.timeout_timer = None  # To keep track of the recording timeout timer

        # Bind a method to update the status
        self.update_status("Idle")

        # Tooltips
        self.create_tooltips()

    def create_tooltips(self):
        """Creates tooltips for GUI elements."""
        create_tooltip(self.exit_button, "Click to exit the application gracefully.")
        create_tooltip(self.model_combobox, "Select the Whisper model to use for transcription.")
        if KEY_COMBINATION_CONFIGURABLE:
            create_tooltip(self.save_keys_button, "Save the selected key combination for toggling recording.")
        create_tooltip(self.save_transcription_cb, "Toggle to enable or disable saving transcriptions.")
        create_tooltip(self.save_audio_cb, "Toggle to enable or disable saving audio clips.")

    def show_user_guide(self):
        """Displays the user guide in a new window."""
        try:
            with open(DOCUMENTATION_FILE, 'r') as file:
                content = file.read()
        except FileNotFoundError:
            content = "User guide not found."

        guide_window = tk.Toplevel(self.root)
        guide_window.title("User Guide")
        guide_window.geometry("700x600")
        guide_window.resizable(False, False)

        guide_text = scrolledtext.ScrolledText(guide_window, wrap='word', state='normal')
        guide_text.pack(expand=True, fill='both')
        guide_text.insert(tk.END, content)
        guide_text.config(state='disabled')

    def change_model(self, event):
        """Handles model change from the combobox."""
        global MODEL_NAME, model
        MODEL_NAME = self.model_var.get()
        logging.info(f"Whisper model changed to: {MODEL_NAME}", extra={'correlation_id': correlation_id})
        # Reload the model asynchronously
        threading.Thread(target=self.reload_model, daemon=True).start()

    def reload_model(self):
        """Reloads the selected Whisper model."""
        try:
            if not check_model_exists(MODEL_NAME):
                answer = messagebox.askyesno("Model Not Found", f"The model '{MODEL_NAME}' is not downloaded. Do you want to download it now?")
                if answer:
                    logging.info(f"User opted to download model: {MODEL_NAME}", extra={'correlation_id': correlation_id})
                    model = whisper.load_model(MODEL_NAME)
                    logging.info(f"Whisper model '{MODEL_NAME}' downloaded and loaded successfully.", extra={'correlation_id': correlation_id})
                    messagebox.showinfo("Model Loaded", f"Whisper model '{MODEL_NAME}' downloaded and loaded successfully.")
                else:
                    logging.warning(f"User declined to download model: {MODEL_NAME}", extra={'correlation_id': correlation_id})
                    messagebox.showwarning("Model Not Loaded", f"Whisper model '{MODEL_NAME}' is not loaded.")
                    return
            else:
                model = whisper.load_model(MODEL_NAME)
                logging.info(f"Whisper model '{MODEL_NAME}' loaded successfully.", extra={'correlation_id': correlation_id})
                messagebox.showinfo("Model Loaded", f"Whisper model '{MODEL_NAME}' loaded successfully.")
        except Exception as e:
            logging.error(f"Failed to load Whisper model '{MODEL_NAME}': {e}", extra={'correlation_id': correlation_id})
            messagebox.showerror("Error", f"Failed to load Whisper model '{MODEL_NAME}': {e}")

    def save_key_combination(self):
        """Saves the selected key combination to the config file."""
        selected_keys = [key for key, var in self.key_vars.items() if var.get()]
        if not selected_keys:
            messagebox.showwarning("No Keys Selected", "Please select at least one key for the key combination.")
            return

        global KEY_COMBINATION
        KEY_COMBINATION = selected_keys

        # Update the config.yml file
        config['key_combination'] = KEY_COMBINATION
        with open(get_absolute_path("config.yml"), 'w') as file:
            yaml.dump(config, file)

        logging.info(f"Key combination updated to: {' + '.join(KEY_COMBINATION)}", extra={'correlation_id': correlation_id})
        messagebox.showinfo("Key Combination Saved", f"Key combination set to: {' + '.join(KEY_COMBINATION)}")

        # Update instructions label
        keys = ' + '.join([key.upper() for key in KEY_COMBINATION])
        self.instructions_label.config(text=f"Press '{keys}' to toggle recording.")

        # Restart key listener with the new key combination
        restart_key_listener(self)

    def toggle_save_transcription(self):
        """Toggles transcription saving on or off based on the config."""
        global SAVE_TRANSCRIPTION
        SAVE_TRANSCRIPTION = self.save_transcription_var.get()
        config['save_transcription'] = SAVE_TRANSCRIPTION
        with open(get_absolute_path("config.yml"), 'w') as file:
            yaml.dump(config, file)
        logging.info(f"Transcription saving toggled to: {'Enabled' if SAVE_TRANSCRIPTION else 'Disabled'}", extra={'correlation_id': correlation_id})

    def toggle_save_audio(self):
        """Toggles audio saving on or off based on the config."""
        global SAVE_AUDIO
        SAVE_AUDIO = self.save_audio_var.get()
        config['save_audio'] = SAVE_AUDIO
        with open(get_absolute_path("config.yml"), 'w') as file:
            yaml.dump(config, file)
        logging.info(f"Audio saving toggled to: {'Enabled' if SAVE_AUDIO else 'Disabled'}", extra={'correlation_id': correlation_id})

    def update_status(self, status):
        """Updates the status label in the GUI."""
        self.status_label.config(text=f"Status: {status}")
        self.root.update()

    def append_transcription(self, text):
        """Appends transcribed text to the GUI and updates the transcription length."""
        self.transcription_text.config(state='normal')
        self.transcription_text.insert(tk.END, text + '\n')
        self.transcription_text.config(state='disabled')
        length = len(self.transcription_text.get("1.0", tk.END).strip())
        self.status_label.config(text=f"Transcription length: {length} characters")
        self.root.update()

    def start_progress(self):
        """Starts the progress bar."""
        if PROGRESS_BAR_ENABLED:
            self.progress.start()

    def stop_progress(self):
        """Stops the progress bar."""
        if PROGRESS_BAR_ENABLED:
            self.progress.stop()

    def on_exit(self):
        """Handles the exit button click event for graceful shutdown."""
        global should_exit
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            logging.info("Application closed by user.", extra={'correlation_id': correlation_id})
            should_exit = True
            self.cancel_timeout_timer()  # Cancel any active timers
            self.exit_button.config(state='disabled')  # Disable the button to prevent multiple clicks
            self.root.quit()

    def start_timeout_timer(self):
        """Starts the recording timeout timer."""
        self.timeout_timer = threading.Timer(RECORDING_TIMEOUT, self.timeout_stop_recording)
        self.timeout_timer.start()
        logging.info(f"Recording timeout set to {RECORDING_TIMEOUT} seconds.", extra={'correlation_id': correlation_id})

    def cancel_timeout_timer(self):
        """Cancels the recording timeout timer if it exists."""
        if self.timeout_timer is not None:
            self.timeout_timer.cancel()
            self.timeout_timer = None
            logging.info("Recording timeout timer cancelled.", extra={'correlation_id': correlation_id})

    def timeout_stop_recording(self):
        """Stops recording due to timeout."""
        logging.info(f"Recording stopped automatically after {RECORDING_TIMEOUT} seconds timeout.", extra={'correlation_id': correlation_id})
        stop_recording(self)

# --------------------- Tooltip Helper Class ---------------------

class CreateToolTip(object):
    """
    Create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     # milliseconds
        self.wraplength = 300   # pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)

    def showtip(self, event=None):
        """Display text in tooltip window"""
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)  # removes all window managers
        self.tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         wraplength=self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()

def create_tooltip(widget, text):
    """Utility function to create tooltips."""
    CreateToolTip(widget, text)

# --------------------- Transcription Logic ---------------------

def load_whisper_model():
    """Loads the Whisper model."""
    try:
        logging.info(f"Loading Whisper model: {MODEL_NAME}", extra={'correlation_id': correlation_id})
        model = whisper.load_model(MODEL_NAME, download_root=None)  # Removed 'weights_only' parameter
        logging.info("Whisper model loaded successfully.", extra={'correlation_id': correlation_id})
        return model
    except Exception as e:
        logging.error(f"Failed to load Whisper model: {e}", extra={'correlation_id': correlation_id}, exc_info=True)
        messagebox.showerror("Error", f"Failed to load Whisper model: {e}")
        exit(1)

# Load initial Whisper model
model = load_whisper_model()

# Global variables
audio_buffer = []
lock = threading.Lock()
should_exit = False  # For thread control
listener_thread = None  # To be initialized in main
timeout_lock = threading.Lock()  # To protect access to the timer

# Progress bar control
transcription_thread = None

def get_timestamp():
    """Returns current timestamp in 'MM-DD-YYYY_HH-MM-SS' format."""
    return datetime.now().strftime("%m-%d-%Y_%H-%M-%S")

def check_model_exists(model_name):
    """Checks if the Whisper model is already downloaded."""
    # Whisper models are typically stored in the cache directory
    cache_dir = os.path.expanduser("~/.cache/whisper")
    model_path = os.path.join(cache_dir, model_name + ".pt")
    return os.path.isfile(model_path)

def clear_buffer_if_needed():
    """Clears the audio buffer if it exceeds the maximum duration."""
    global audio_buffer
    # Calculate total duration based on frames per buffer
    total_frames = sum(len(chunk) for chunk in audio_buffer)
    duration = total_frames / SAMPLERATE
    if duration > BUFFER_MAX_DURATION:
        logging.warning("Buffer limit exceeded, clearing buffer.", extra={'correlation_id': correlation_id})
        audio_buffer.clear()

def start_recording(gui):
    """Starts recording audio."""
    if not RECORD_AUDIO:
        logging.info("Audio recording is disabled via configuration.", extra={'correlation_id': correlation_id})
        return
    play_start_sound()
    with lock:
        if not gui.is_recording:
            gui.is_recording = True
            audio_buffer.clear()
            gui.update_status("Recording")
            logging.info("Recording started.", extra={'correlation_id': correlation_id})
            gui.start_timeout_timer()  # Start the timeout timer

def stop_recording(gui):
    """Stops recording and initiates transcription."""
    if not gui.is_recording:
        return
    play_stop_sound()
    with lock:
        if gui.is_recording:
            gui.is_recording = False
            gui.update_status("Transcribing")
            gui.cancel_timeout_timer()  # Cancel the timeout timer
            logging.info("Recording stopped. Starting transcription.", extra={'correlation_id': correlation_id})
            if audio_buffer:
                # Concatenate and flatten the audio data
                audio_data = np.concatenate(audio_buffer, axis=0).flatten()
                # Start transcription in a separate thread to avoid blocking the GUI
                transcription_thread = threading.Thread(target=transcribe_audio, args=(audio_data, gui), daemon=True)
                transcription_thread.start()
            else:
                logging.warning("No audio data captured.", extra={'correlation_id': correlation_id})
                gui.update_status("Idle")
            audio_buffer.clear()

def transcribe_audio(audio_data, gui):
    """Transcribes the audio data and updates the GUI."""
    try:
        # Start progress bar
        gui.start_progress()

        # Transcribe the audio
        # Whisper expects audio in float32 format
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)

        result = model.transcribe(audio_data, fp16=USE_FP16)
        transcription = result['text'].strip()
        logging.info(f"Transcription: {transcription}", extra={'correlation_id': correlation_id})

        # Update GUI with transcription
        if transcription:
            gui.append_transcription(transcription)
            if SAVE_TRANSCRIPTION:
                save_transcription(transcription)
            pyautogui.write(transcription + ' ')
            logging.info("Transcription typed out on screen.", extra={'correlation_id': correlation_id})

            if SAVE_AUDIO and SOUND_FILE_AVAILABLE:
                save_audio_clip(audio_data)

        # Log system usage after transcription
        if ENABLE_SYSTEM_MONITORING:
            log_system_usage()

        # Update GUI status
        gui.update_status("Idle")
    except Exception as e:
        logging.error(f"Error during transcription: {e}", extra={'correlation_id': correlation_id}, exc_info=True)
        gui.update_status("Error")
        messagebox.showerror("Error", f"Transcription failed: {e}")
    finally:
        # Stop progress bar
        gui.stop_progress()

def save_transcription(transcription):
    """Saves the transcription to a file."""
    try:
        timestamp = get_timestamp()
        transcription_file = os.path.join(SAVE_DIR, f"transcription_{timestamp}.txt")
        with open(transcription_file, 'w', encoding='utf-8') as f:
            f.write(transcription)
        logging.info(f"Transcription saved to {transcription_file}", extra={'correlation_id': correlation_id})
    except Exception as e:
        logging.error(f"Failed to save transcription: {e}", extra={'correlation_id': correlation_id}, exc_info=True)
        messagebox.showerror("Error", f"Failed to save transcription: {e}")

def save_audio_clip(audio_data):
    """Saves the recorded audio clip to a file."""
    try:
        timestamp = get_timestamp()
        audio_file = os.path.join(SAVE_DIR, f"audio_{timestamp}.wav")
        # Normalize audio to prevent clipping
        audio_normalized = audio_data / np.max(np.abs(audio_data)) if np.max(np.abs(audio_data)) != 0 else audio_data
        sf.write(audio_file, audio_normalized, SAMPLERATE)
        logging.info(f"Audio clip saved to {audio_file}", extra={'correlation_id': correlation_id})
    except Exception as e:
        logging.error(f"Failed to save audio clip: {e}", extra={'correlation_id': correlation_id}, exc_info=True)
        messagebox.showerror("Error", f"Failed to save audio clip: {e}")

def audio_callback(indata, frames, time_info, status, gui):
    """Callback function to capture audio data."""
    try:
        if gui.is_recording:
            with lock:
                audio_buffer.append(indata.copy())
            logging.debug(f"Captured {len(indata)} frames of audio.", extra={'correlation_id': correlation_id})
            clear_buffer_if_needed()
    except Exception as e:
        logging.error(f"Error in audio callback: {e}", extra={'correlation_id': correlation_id}, exc_info=True)
        gui.update_status("Error")
        messagebox.showerror("Error", f"Error during audio capture: {e}")

def key_listener(gui):
    """Listens for the key combination to toggle recording."""
    keys = KEY_COMBINATION
    logging.info(f"Key listener started. Waiting for {' + '.join(keys)} to toggle recording.", extra={'correlation_id': correlation_id})
    while not should_exit:
        try:
            if all(keyboard.is_pressed(key) for key in keys):
                if not gui.is_recording:
                    start_recording(gui)
                else:
                    stop_recording(gui)
                # Wait until keys are released to avoid multiple toggles
                while all(keyboard.is_pressed(key) for key in keys):
                    time.sleep(KEY_LISTENER_SLEEP)
            time.sleep(KEY_LISTENER_SLEEP)
        except Exception as e:
            logging.error(f"Error in key listener: {e}", extra={'correlation_id': correlation_id}, exc_info=True)
            gui.update_status("Error")
            messagebox.showerror("Error", f"Key listener failed: {e}")

def play_start_sound():
    """Plays a beep sound when recording starts."""
    winsound.Beep(1000, 200)  # Frequency 1000 Hz, Duration 200 ms

def play_stop_sound():
    """Plays a beep sound when recording stops."""
    winsound.Beep(600, 200)  # Frequency 600 Hz, Duration 200 ms

def log_system_usage():
    """Logs system resource usage."""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    cpu_usage = process.cpu_percent(interval=1)
    logging.info(f"Memory usage: {memory_info.rss / (1024 * 1024):.2f} MB, CPU usage: {cpu_usage:.2f}%", extra={'correlation_id': correlation_id})

def system_monitoring():
    """Periodically logs system resource usage."""
    while not should_exit:
        try:
            log_system_usage()
            time.sleep(SYSTEM_MONITORING_INTERVAL)
        except Exception as e:
            logging.error(f"Error in system monitoring: {e}", extra={'correlation_id': correlation_id}, exc_info=True)

# --------------------- Handling Optional soundfile Import ---------------------

# Attempt to import soundfile
try:
    import soundfile as sf
    SOUND_FILE_AVAILABLE = True
except ImportError:
    logging.warning("soundfile library not installed. Audio will not be saved.", extra={'correlation_id': correlation_id})
    SOUND_FILE_AVAILABLE = False

# --------------------- Main Function ---------------------

def main():
    """Main function to run the transcription GUI and audio stream."""
    global listener_thread  # Declare as global to modify within the function

    # Initialize GUI
    root = tk.Tk()
    gui = TranscriptionGUI(root)

    # Start key listener thread
    listener_thread = threading.Thread(target=key_listener, args=(gui,), daemon=True)
    listener_thread.start()

    # Start system resource monitoring thread if enabled
    if ENABLE_SYSTEM_MONITORING:
        system_monitor_thread = threading.Thread(target=system_monitoring, daemon=True)
        system_monitor_thread.start()

    # Start audio input stream
    try:
        with sd.InputStream(
            callback=lambda indata, frames, time_info, status: audio_callback(indata, frames, time_info, status, gui),
            samplerate=SAMPLERATE,
            channels=CHANNELS,
            dtype=DTYPE
        ):
            logging.info("Audio input stream started.", extra={'correlation_id': correlation_id})
            gui.update_status("Idle")
            root.mainloop()
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt: Application terminated by user.", extra={'correlation_id': correlation_id})
    except Exception as e:
        logging.error(f"Failed to start audio input stream: {e}", extra={'correlation_id': correlation_id}, exc_info=True)
        messagebox.showerror("Error", f"Failed to start audio input stream: {e}")
        exit(1)
    finally:
        logging.info("Application has exited gracefully.", extra={'correlation_id': correlation_id})

def restart_key_listener(gui):
    """Restarts the key listener to apply new key combinations."""
    global listener_thread
    # Signal to exit the current key listener
    global should_exit
    should_exit = True
    listener_thread.join()
    should_exit = False
    # Start a new key listener thread with updated key combination
    listener_thread = threading.Thread(target=key_listener, args=(gui,), daemon=True)
    listener_thread.start()

if __name__ == "__main__":
    main()
