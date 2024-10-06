# main.py

import logging
import subprocess
import tkinter as tk
from tkinter import messagebox
import threading
import traceback
import psutil
import numpy as np
import time
import sys
import os
import uuid
import torch
import sounddevice as sd
import winsound
import pyautogui
import keyboard
from datetime import datetime

# Import your custom modules
from config import load_config, save_config, ConfigError
from app_logging.setup import setup_logging, set_log_level
from transcription.transcriber import load_whisper_model
from gui.transcription_gui import TranscriptionGUI
from audio import start_audio_stream, save_audio_clip, save_transcription, AudioProcessingError
from state import state
import noisereduce as nr
from utils.file_utils import get_absolute_path
from utils.gui_utils import create_tooltip
from utils.logging_utils import sanitize_message
from utils.helpers import graceful_shutdown, load_model_with_retry

# Suppress verbose numba logging
numba_logger = logging.getLogger('numba')
numba_logger.setLevel(logging.WARNING)

# Initialize global variables
lock = threading.Lock()
audio_buffer = []
should_exit = False
logger = logging.getLogger(__name__)

# Generate a unique trace_id for this session
trace_id = str(uuid.uuid4())
state.trace_id = trace_id  # Assign trace_id to state object

# Load configuration globally for access in all functions
try:
    config = load_config()
except ConfigError as e:
    # Show error message if configuration fails to load
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    messagebox.showerror("Configuration Error", f"Failed to load configuration: {e}")
    sys.exit(1)

# Set up logging
setup_logging(config, state.correlation_id, state.trace_id)

# Retry decorator to retry a function on failure
def retry_on_failure(retries=3, delay=1):
    """
    Decorator to retry a function upon failure.

    Args:
        retries (int): Number of times to retry.
        delay (int): Delay between retries in seconds.

    Returns:
        The wrapped function with retry capability.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    sanitized_error = sanitize_message(str(e))
                    logger.error(
                        f"Retrying due to error: {sanitized_error}, Attempt {attempt + 1} of {retries}",
                        extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id}
                    )
                    time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator

@retry_on_failure()
def load_model_with_retry_decorator(model_name):
    """
    Attempts to load the model with retries.

    Args:
        model_name (str): Name of the model to load.

    Returns:
        The loaded model.
    """
    return load_model_with_retry(model_name, logger, state.correlation_id, state.trace_id)

# Error handling function for unexpected errors
def handle_unexpected_error(type, value, traceback_obj):
    """
    Handles unexpected errors by logging them and generating a crash report.

    Args:
        type: Exception type.
        value: Exception value.
        traceback_obj: Traceback object.
    """
    sanitized_value = sanitize_message(str(value))
    logger.critical(
        f"Unexpected error: {sanitized_value}",
        exc_info=(type, value, traceback_obj),
        extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id}
    )

    # Generate crash report
    crash_report = f"Exception Type: {type.__name__}\nException Value: {sanitized_value}\n"
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
    root.withdraw()  # Hide the root window
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
                extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id},
                exc_info=True
            )
    graceful_shutdown()

# Hook into the system's exception handler
sys.excepthook = handle_unexpected_error

def check_dependencies(config, gui):
    """
    Checks if all required dependencies are available.

    Args:
        config: Configuration object.
        gui: GUI instance.
    """
    try:
        # Check if audio input device is available
        devices = sd.query_devices()
        if not devices:
            raise AudioProcessingError("No audio devices found.")
        default_input = sd.default.device[0]
        if default_input is None:
            raise AudioProcessingError("No default audio input device set.")
        logger.info("Audio input device is available.", extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id})
    except Exception as e:
        sanitized_error = sanitize_message(str(e))
        logger.error(
            f"Dependency check failed: {sanitized_error}",
            extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id},
            exc_info=True
        )
        # Schedule the shutdown to run in the main thread
        schedule_graceful_shutdown(
            gui,
            lambda e=e: messagebox.showerror("Dependency Error", f"Audio input device not available: {e}")
        )

def play_start_sound():
    """
    Plays a beep sound when recording starts.
    """
    try:
        winsound.Beep(1000, 200)  # Frequency 1000 Hz, Duration 200 ms
    except:
        pass  # Non-Windows systems might not support winsound

def play_stop_sound():
    """
    Plays a beep sound when recording stops.
    """
    try:
        winsound.Beep(600, 200)  # Frequency 600 Hz, Duration 200 ms
    except:
        pass  # Non-Windows systems might not support winsound

def schedule_graceful_shutdown(gui, error_callback=None):
    """
    Schedules the graceful shutdown to run in the main thread.

    Args:
        gui: GUI instance.
        error_callback: Optional callback to execute before shutdown.
    """
    if error_callback:
        gui.root.after(0, error_callback)
    gui.root.after(0, graceful_shutdown)

def log_system_usage():
    """
    Logs system resource usage periodically.
    """
    while not should_exit:
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        cpu_usage = process.cpu_percent(interval=1)
        logger.info(
            f"Memory usage: {memory_info.rss / (1024 * 1024):.2f} MB, CPU usage: {cpu_usage:.2f}%",
            extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id}
        )
        time.sleep(60)  # Log every 60 seconds

def audio_callback(indata, frames, time_info, status, gui):
    """
    Callback function to capture audio data.

    Args:
        indata: Input audio data.
        frames: Number of frames.
        time_info: Time information.
        status: Callback status.
        gui: GUI instance.
    """
    try:
        if gui.is_recording:
            with lock:
                audio_buffer.append(indata.copy())
            # Update the waveform visualization
            gui.update_waveform(indata.copy())
            logger.debug(
                f"Captured {len(indata)} frames of audio.",
                extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id}
            )
    except Exception as e:
        sanitized_error = sanitize_message(str(e))
        logger.error(
            f"Error in audio callback: {sanitized_error}",
            extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id},
            exc_info=True
        )
        gui.root.after(0, lambda: gui.update_status("Error"))
        gui.root.after(0, lambda: messagebox.showerror("Error", f"Error during audio capture: {e}"))

def start_recording(gui, config):
    """
    Starts recording audio.

    Args:
        gui: GUI instance.
        config: Configuration object.
    """
    if not config.record_audio:
        logger.info("Audio recording is disabled via configuration.", extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id})
        return
    play_start_sound()
    with lock:
        if not gui.is_recording:
            gui.is_recording = True
            audio_buffer.clear()
            gui.update_status("Recording")
            logger.info("Recording started.", extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id})
            gui.start_timeout_timer()

def stop_recording(gui):
    """
    Stops recording and initiates transcription.

    Args:
        gui: GUI instance.
    """
    if not gui.is_recording:
        return
    play_stop_sound()
    with lock:
        if gui.is_recording:
            gui.is_recording = False
            gui.update_status("Transcribing")
            gui.stop_timeout_timer()
            logger.info("Recording stopped. Starting transcription.", extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id})
            if audio_buffer:
                audio_data = np.concatenate(audio_buffer, axis=0).flatten()
                transcription_thread = threading.Thread(target=transcribe_audio, args=(audio_data, gui), daemon=True)
                transcription_thread.start()
            else:
                logger.warning("No audio data captured.", extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id})
                gui.update_status("Idle")
            audio_buffer.clear()

def transcribe_audio(audio_data, gui):
    """
    Transcribes the audio data and updates the GUI.

    Args:
        audio_data: Captured audio data.
        gui: GUI instance.
    """
    try:
        gui.root.after(0, gui.start_progress)
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)
        noise_reduction_enabled = config.enable_noise_reduction
        if noise_reduction_enabled:
            logger.info("Applying noise reduction...", extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id})
            noise_sample = audio_data[:int(0.5 * config.samplerate)]
            audio_data = nr.reduce_noise(y=audio_data, sr=config.samplerate, y_noise=noise_sample)
        model_device = gui.model.device
        audio_tensor = torch.from_numpy(audio_data).to(model_device)
        # Perform transcription
        result = gui.model.transcribe(audio_tensor, fp16=config.use_fp16)
        transcription = result['text'].strip()
        logger.info(f"Transcription: {transcription}", extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id})
        if transcription:
            gui.root.after(0, lambda: gui.append_transcription(transcription))
            if config.save_transcription:
                save_transcription(transcription, config.save_directory, state.correlation_id, gui)
            # Simulate typing the transcription
            pyautogui.write(transcription + ' ')
        if config.save_audio:
            save_audio_clip(audio_data, config.save_directory, config.samplerate, state.correlation_id, gui)
        # Log system usage once, without blocking
        if config.enable_system_monitoring:
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            cpu_usage = process.cpu_percent(interval=0.1)
            logger.info(
                f"Memory usage after transcription: {memory_info.rss / (1024 * 1024):.2f} MB, CPU usage: {cpu_usage:.2f}%",
                extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id}
            )
        gui.root.after(0, lambda: gui.update_status("Idle"))
    except Exception as e:
        sanitized_error = sanitize_message(str(e))
        logger.error(
            f"Error during transcription: {sanitized_error}",
            extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id},
            exc_info=True
        )
        gui.root.after(0, lambda: gui.update_status("Error"))
        gui.root.after(0, lambda: messagebox.showerror("Error", f"Transcription failed: {e}"))
    finally:
        gui.root.after(0, gui.stop_progress)

def key_listener(gui, config):
    """
    Listens for the key combination to toggle recording.

    Args:
        gui: GUI instance.
        config: Configuration object.
    """
    keys = config.key_combination
    logger.info(
        f"Key listener started. Waiting for {' + '.join(keys)} to toggle recording.",
        extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id}
    )
    while not should_exit:
        try:
            if all(keyboard.is_pressed(key) for key in keys):
                if not gui.is_recording:
                    gui.root.after(0, lambda: start_recording(gui, config))
                else:
                    gui.root.after(0, lambda: stop_recording(gui))
                # Wait until the keys are released to prevent multiple toggles
                while all(keyboard.is_pressed(key) for key in keys):
                    time.sleep(config.key_listener_sleep)
            time.sleep(config.key_listener_sleep)
        except Exception as e:
            sanitized_error = sanitize_message(str(e))
            logger.error(
                f"Error in key listener: {sanitized_error}",
                extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id},
                exc_info=True
            )
            gui.root.after(0, lambda: gui.update_status("Error"))
            gui.root.after(0, lambda: messagebox.showerror("Error", f"Key listener failed: {e}"))

def load_model_in_thread(model_name, gui):
    """
    Loads the Whisper model in a separate thread to avoid blocking the main GUI thread.

    Args:
        model_name (str): The name of the model to load.
        gui: The GUI instance to update the status.
    """
    def load_model():
        try:
            # Schedule GUI updates in the main thread
            gui.root.after(0, gui.update_status, "Loading Model")
            model = load_model_with_retry_decorator(model_name)
            gui.root.after(0, gui.set_model, model)
            gui.root.after(0, gui.update_status, "Idle")
            logger.info(f"Model '{model_name}' loaded successfully.", extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id})
        except Exception as e:
            sanitized_error = sanitize_message(str(e))
            logger.error(
                f"Failed to load model '{model_name}': {sanitized_error}",
                extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id},
                exc_info=True
            )
            gui.root.after(0, gui.update_status, "Error")
            # Capture the exception message
            exception_message = str(e)
            gui.root.after(0, lambda: messagebox.showerror("Model Load Error", f"Failed to load model '{model_name}'.\nError: {exception_message}"))

    threading.Thread(target=load_model, daemon=True).start()


def set_log_level_callback(level):
    """
    Callback function to set the log level.

    Args:
        level (str): The new log level.
    """
    set_log_level(level)

# Main execution block
if __name__ == "__main__":
    try:
        # Initialize the main GUI window
        root = tk.Tk()
        gui = TranscriptionGUI(
            root=root,
            config=config,
            model=None,  # Initial model is None; will be set after loading
            stop_recording_callback=lambda: stop_recording(gui),
            correlation_id=state.correlation_id,
            trace_id=state.trace_id,
            on_model_change_callback=None,  # Implement if needed
            graceful_shutdown_callback=graceful_shutdown,
            set_log_level_callback=set_log_level_callback  # Provide the log level callback
        )

        def schedule_model_loading():
            """
            Schedules the model loading after the GUI is initialized.
            """
            default_model_name = config.model_support.default_model
            load_model_in_thread(default_model_name, gui)

        # Schedule tasks after the GUI main loop starts
        root.after(100, schedule_model_loading)
        root.after(200, lambda: check_dependencies(config, gui))

        try:
            # Get the audio device index
            device_index = config.audio_device_index or sd.default.device[0]
            # Start the audio input stream
            stream = start_audio_stream(
                callback=lambda indata, frames, time_info, status: audio_callback(indata, frames, time_info, status, gui),
                samplerate=config.samplerate,
                channels=config.channels,
                dtype=config.dtype,
                device=device_index,
                gui=gui  # Pass the GUI instance for notifications
            )
            logger.info("Audio stream started successfully.", extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id})
        except AudioProcessingError as e:
            sanitized_error = sanitize_message(str(e))
            logger.error(
                f"Failed to start audio input stream: {sanitized_error}",
                extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id},
                exc_info=True
            )
            schedule_graceful_shutdown(
                gui,
                lambda e=e: messagebox.showerror("Error", f"Failed to start audio input stream: {e}")
            )

        # Start the key listener thread
        listener_thread = threading.Thread(target=key_listener, args=(gui, config), daemon=True)
        listener_thread.start()

        # Start the system monitoring thread if enabled
        if config.enable_system_monitoring:
            system_monitor_thread = threading.Thread(target=log_system_usage, daemon=True)
            system_monitor_thread.start()

        # Set the command for the exit button to gracefully shutdown
        gui.exit_button.config(command=graceful_shutdown)
        # Start the GUI main loop
        root.mainloop()
    except Exception as e:
        logger.critical(f"Fatal error in main execution: {e}", exc_info=True)
        graceful_shutdown()
