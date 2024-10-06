import tkinter as tk
from tkinter import messagebox  # Add this import
import threading
import logging
from config import load_config, save_config, ConfigError
from app_logging.setup import setup_logging, set_log_level  # Adjusted import
from transcription.transcriber import load_whisper_model  # Adjusted import
from gui.main_gui import TranscriptionGUI  # Adjusted import
from audio import start_audio_stream, save_audio_clip, AudioProcessingError  # Adjusted import
import keyboard
import pyautogui
import numpy as np
import time
import psutil
import sys
import winsound  # For sound
from datetime import datetime
import os
import sounddevice as sd
from state.state_manager import state  # Adjusted import
import noisereduce as nr
from utils.file_utils import get_absolute_path  # Adjusted import
from utils.gui_utils import create_tooltip  # Adjusted import
from utils.logging_utils import sanitize_message  # Adjusted import
import subprocess
import torch
import uuid
from utils.helpers import graceful_shutdown, load_model_with_retry  # Adjusted import

# Initialize global variables
lock = threading.Lock()  # Initialize lock
audio_buffer = []  # Initialize audio buffer
should_exit = False  # Initialize exit flag

# Set up module-specific logger
logger = logging.getLogger(__name__)

# Generate a trace_id
trace_id = str(uuid.uuid4())

# Retry decorator to retry function on failure
def retry_on_failure(retries=3, delay=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None  # Keep track of the last exception
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    sanitized_error = sanitize_message(str(e))
                    logger.error(
                        f"Retrying due to error: {sanitized_error}, Attempt {attempt + 1} of {retries}",
                        extra={'correlation_id': state.correlation_id, 'trace_id': trace_id}
                    )
                    time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator

@retry_on_failure()
def load_model_with_retry_decorator(model_name):
    """Attempts to load the model with retries."""
    return load_model_with_retry(model_name, logger, state.correlation_id, trace_id)

# Error handling
def handle_unexpected_error(type, value, traceback_obj):
    """Handles unexpected errors by logging them and generating a crash report."""
    sanitized_value = sanitize_message(str(value))  # Define sanitized_value
    logger.critical(
        f"Unexpected error: {sanitized_value}",
        exc_info=(type, value, traceback_obj),
        extra={'correlation_id': state.correlation_id, 'trace_id': trace_id}
    )

    # Generate crash report
    crash_report = f"Exception Type: {type.__name__}\nException Value: {sanitized_value}\n"
    import traceback
    crash_report += "".join(traceback.format_tb(traceback_obj))
    # Add system info
    crash_report += "\nSystem Information:\n"
    crash_report += f"Platform: {sys.platform}\n"
    crash_report += f"Python Version: {sys.version}\n"
    # Save crash report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    crash_report_dir = get_absolute_path('crash_reports')
    os.makedirs(crash_report_dir, exist_ok=True)
    crash_report_file = os.path.join(crash_report_dir, f"crash_report_{timestamp}.txt")
    with open(crash_report_file, 'w') as f:
        f.write(crash_report)
    # Prompt user
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    response = messagebox.askyesno(
        "Unexpected Error",
        f"An unexpected error occurred: {sanitized_value}\nA crash report has been saved to {crash_report_file}.\nWould you like to view the crash report?"
    )
    if response:
        try:
            if sys.platform.startswith('win'):
                os.startfile(crash_report_file)
            elif sys.platform.startswith('darwin'):
                subprocess.call(('open', crash_report_file))
            else:
                subprocess.call(('xdg-open', crash_report_file))
        except Exception as e:
            sanitized_error = sanitize_message(str(e))
            logger.error(
                f"Failed to open crash report: {sanitized_error}",
                extra={'correlation_id': state.correlation_id, 'trace_id': trace_id},
                exc_info=True
            )
    graceful_shutdown()

# Hook into the system's exception handler
sys.excepthook = handle_unexpected_error

def check_dependencies(config, gui):
    """Checks if all required dependencies are available."""
    try:
        # Check if audio input device is available
        devices = sd.query_devices()
        if not devices:
            raise AudioProcessingError("No audio devices found.")
        default_input = sd.default.device[0]
        if default_input is None:
            raise AudioProcessingError("No default audio input device set.")
        logger.info("Audio input device is available.", extra={'correlation_id': state.correlation_id, 'trace_id': trace_id})
    except Exception as e:
        sanitized_error = sanitize_message(str(e))
        logger.error(
            f"Dependency check failed: {sanitized_error}",
            extra={'correlation_id': state.correlation_id, 'trace_id': trace_id},
            exc_info=True
        )
        schedule_graceful_shutdown(gui, lambda e=e: messagebox.showerror("Dependency Error", f"Audio input device not available: {e}"))

def play_start_sound():
    """Plays a beep sound when recording starts."""
    try:
        winsound.Beep(1000, 200)  # Frequency 1000 Hz, Duration 200 ms
    except:
        pass  # Non-Windows systems might not support winsound

def play_stop_sound():
    """Plays a beep sound when recording stops."""
    try:
        winsound.Beep(600, 200)  # Frequency 600 Hz, Duration 200 ms
    except:
        pass  # Non-Windows systems might not support winsound

def schedule_graceful_shutdown(gui, error_callback=None):
    """Schedules the graceful shutdown to run in the main thread."""
    if error_callback:
        gui.root.after(0, error_callback)
    gui.root.after(0, graceful_shutdown)

def log_system_usage():
    """Logs system resource usage."""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    cpu_usage = process.cpu_percent(interval=1)
    logger.info(
        f"Memory usage: {memory_info.rss / (1024 * 1024):.2f} MB, CPU usage: {cpu_usage:.2f}%",
        extra={'correlation_id': state.correlation_id, 'trace_id': trace_id}
    )

# Other parts of your main.py remain unchanged...


    # Generate crash report
    crash_report = f"Exception Type: {type.__name__}\nException Value: {sanitized_value}\n"
    import traceback
    crash_report += "".join(traceback.format_tb(traceback_obj))
    # Add system info
    crash_report += "\nSystem Information:\n"
    crash_report += f"Platform: {sys.platform}\n"
    crash_report += f"Python Version: {sys.version}\n"
    # Save crash report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    crash_report_dir = get_absolute_path('crash_reports')
    os.makedirs(crash_report_dir, exist_ok=True)
    crash_report_file = os.path.join(crash_report_dir, f"crash_report_{timestamp}.txt")
    with open(crash_report_file, 'w') as f:
        f.write(crash_report)
    # Prompt user
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    response = messagebox.askyesno(
        "Unexpected Error",
        f"An unexpected error occurred: {sanitized_value}\nA crash report has been saved to {crash_report_file}.\nWould you like to view the crash report?"
    )
    if response:
        try:
            if sys.platform.startswith('win'):
                os.startfile(crash_report_file)
            elif sys.platform.startswith('darwin'):
                subprocess.call(('open', crash_report_file))
            else:
                subprocess.call(('xdg-open', crash_report_file))
        except Exception as e:
            sanitized_error = sanitize_message(str(e))
            logger.error(
                f"Failed to open crash report: {sanitized_error}",
                extra={'correlation_id': state.correlation_id, 'trace_id': trace_id},
                exc_info=True
            )
    graceful_shutdown()

# Hook into the system's exception handler
sys.excepthook = handle_unexpected_error

def check_dependencies(config, gui):
    """Checks if all required dependencies are available."""
    try:
        # Check if audio input device is available
        devices = sd.query_devices()
        if not devices:
            raise AudioProcessingError("No audio devices found.")
        default_input = sd.default.device[0]
        if default_input is None:
            raise AudioProcessingError("No default audio input device set.")
        logger.info("Audio input device is available.", extra={'correlation_id': state.correlation_id, 'trace_id': trace_id})
    except Exception as e:
        sanitized_error = sanitize_message(str(e))
        logger.error(
            f"Dependency check failed: {sanitized_error}",
            extra={'correlation_id': state.correlation_id, 'trace_id': trace_id},
            exc_info=True
        )
        # Schedule the shutdown to run in the main thread
        schedule_graceful_shutdown(
            gui,
            lambda e=e: messagebox.showerror("Dependency Error", f"Audio input device not available: {e}")
        )

def audio_callback(indata, frames, time_info, status, gui):
    """Callback function to capture audio data."""
    try:
        if gui.is_recording:
            with lock:
                audio_buffer.append(indata.copy())
            # Avoid logging here unless necessary
            logger.debug(
                f"Captured {len(indata)} frames of audio.",
                extra={'correlation_id': state.correlation_id, 'trace_id': trace_id}
            )
    except Exception as e:
        sanitized_error = sanitize_message(str(e))
        logger.error(
            f"Error in audio callback: {sanitized_error}",
            extra={'correlation_id': state.correlation_id, 'trace_id': trace_id},
            exc_info=True
        )
        gui.root.after(0, lambda: gui.update_status("Error"))
        gui.root.after(0, lambda: messagebox.showerror("Error", f"Error during audio capture: {e}"))

def start_recording(gui, config):
    """Starts recording audio."""
    if not config.get('record_audio', True):
        logger.info("Audio recording is disabled via configuration.", extra={'correlation_id': state.correlation_id, 'trace_id': trace_id})
        return
    play_start_sound()
    with lock:
        if not gui.is_recording:
            gui.is_recording = True
            audio_buffer.clear()
            gui.update_status("Recording")
            logger.info("Recording started.", extra={'correlation_id': state.correlation_id, 'trace_id': trace_id})
            gui.start_timeout_timer()

def stop_recording(gui):
    """Stops recording and initiates transcription."""
    if not gui.is_recording:
        return
    play_stop_sound()
    with lock:
        if gui.is_recording:
            gui.is_recording = False
            gui.update_status("Transcribing")
            gui.stop_timeout_timer()
            logger.info("Recording stopped. Starting transcription.", extra={'correlation_id': state.correlation_id, 'trace_id': trace_id})
            if audio_buffer:
                audio_data = np.concatenate(audio_buffer, axis=0).flatten()
                transcription_thread = threading.Thread(target=transcribe_audio, args=(audio_data, gui), daemon=True)
                transcription_thread.start()
            else:
                logger.warning("No audio data captured.", extra={'correlation_id': state.correlation_id, 'trace_id': trace_id})
                gui.update_status("Idle")
            audio_buffer.clear()

def transcribe_audio(audio_data, gui):
    """Transcribes the audio data and updates the GUI."""
    try:
        gui.root.after(0, gui.start_progress)
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)
        noise_reduction_enabled = config.get('enable_noise_reduction', True)
        if noise_reduction_enabled:
            logger.info("Applying noise reduction...", extra={'correlation_id': state.correlation_id, 'trace_id': trace_id})
            noise_sample = audio_data[:int(0.5 * config.get('samplerate', 16000))]
            audio_data = nr.reduce_noise(y=audio_data, sr=config.get('samplerate', 16000), y_noise=noise_sample)
        model_device = gui.model.device
        audio_tensor = torch.from_numpy(audio_data).to(model_device)
        result = gui.model.transcribe(audio_tensor, fp16=config.get('use_fp16', False))
        transcription = result['text'].strip()
        logger.info(f"Transcription: {transcription}", extra={'correlation_id': state.correlation_id, 'trace_id': trace_id})
        if transcription:
            gui.root.after(0, lambda: gui.append_transcription(transcription))
            if config.get('save_transcription', False):
                save_transcription(transcription, config, gui)
            pyautogui.write(transcription + ' ')
        if config.get('save_audio', False):
            save_audio_clip(audio_data, config.get('save_directory', 'transcriptions'), config.get('samplerate', 16000), state.correlation_id, gui.notify_user)
        if config.get('enable_system_monitoring', True):
            log_system_usage()
        gui.root.after(0, lambda: gui.update_status("Idle"))
    except Exception as e:
        sanitized_error = sanitize_message(str(e))
        logger.error(
            f"Error during transcription: {sanitized_error}",
            extra={'correlation_id': state.correlation_id, 'trace_id': trace_id},
            exc_info=True
        )
        gui.root.after(0, lambda: gui.update_status("Error"))
        gui.root.after(0, lambda: messagebox.showerror("Error", f"Transcription failed: {e}"))
    finally:
        gui.root.after(0, gui.stop_progress)

def key_listener(gui, config):
    """Listens for the key combination to toggle recording."""
    keys = config.get('key_combination', ['ctrl', 'alt', 'space'])
    logger.info(
        f"Key listener started. Waiting for {' + '.join(keys)} to toggle recording.",
        extra={'correlation_id': state.correlation_id, 'trace_id': trace_id}
    )
    while not should_exit:
        try:
            if all(keyboard.is_pressed(key) for key in keys):
                if not gui.is_recording:
                    gui.root.after(0, lambda: start_recording(gui, config))
                else:
                    gui.root.after(0, lambda: stop_recording(gui))
                while all(keyboard.is_pressed(key) for key in keys):
                    time.sleep(config.get('key_listener_sleep', 0.1))
            time.sleep(config.get('key_listener_sleep', 0.1))
        except Exception as e:
            sanitized_error = sanitize_message(str(e))
            logger.error(
                f"Error in key listener: {sanitized_error}",
                extra={'correlation_id': state.correlation_id, 'trace_id': trace_id},
                exc_info=True
            )
            gui.root.after(0, lambda: gui.update_status("Error"))
            gui.root.after(0, lambda: messagebox.showerror("Error", f"Key listener failed: {e}"))

# Main execution
if __name__ == "__main__":
    try:
        config = load_config()
    except ConfigError as e:
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showerror("Configuration Error", f"Failed to load configuration: {e}")
        sys.exit(1)

    setup_logging(config, state.correlation_id, trace_id)
    sys.excepthook = handle_unexpected_error

    root = tk.Tk()
    gui = TranscriptionGUI(
        root,
        config,
        None,
        lambda: stop_recording(gui),
        state.correlation_id,
        trace_id,
        None,
        graceful_shutdown  # Pass the graceful_shutdown function as a callback
    )

    def schedule_model_loading():
        default_model_name = config.get('model_support', {}).get('default_model', 'base')
        load_model_in_thread(default_model_name, gui)

    root.after(100, schedule_model_loading)
    root.after(200, lambda: check_dependencies(config, gui))

    try:
        device_index = config.get('audio_device_index', sd.default.device[0])
        stream = start_audio_stream(
            callback=lambda indata, frames, time_info, status: audio_callback(indata, frames, time_info, status, gui),
            gui_notification_callback=gui.notify_user,
            samplerate=config.get('samplerate', 16000),
            channels=config.get('channels', 1),
            dtype=config.get('dtype', 'float32'),
            device=device_index
        )
        logger.info("Audio stream started successfully.", extra={'correlation_id': state.correlation_id, 'trace_id': trace_id})
    except AudioProcessingError as e:
        sanitized_error = sanitize_message(str(e))
        logger.error(
            f"Failed to start audio input stream: {sanitized_error}",
            extra={'correlation_id': state.correlation_id, 'trace_id': trace_id},
            exc_info=True
        )
        schedule_graceful_shutdown(
            gui,
            lambda e=e: messagebox.showerror("Error", f"Failed to start audio input stream: {e}")
        )

    listener_thread = threading.Thread(target=key_listener, args=(gui, config), daemon=True)
    listener_thread.start()

    if config.get('enable_system_monitoring', True):
        system_monitor_thread = threading.Thread(target=log_system_usage, daemon=True)
        system_monitor_thread.start()

    gui.exit_button.config(command=graceful_shutdown)
    root.mainloop()
