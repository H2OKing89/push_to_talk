# main.py
import tkinter as tk
import threading
import logging
from config import load_config, save_config, ConfigError
from logger import setup_logging
from transcription import load_whisper_model
from gui import TranscriptionGUI
from audio_handler import start_audio_stream, save_audio_clip, AudioProcessingError
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
from state import lock, should_exit, audio_buffer, correlation_id
import noisereduce as nr
from utils import get_absolute_path, create_tooltip  # Added create_tooltip import
import subprocess  # Added import for subprocess
import torch  # Import torch for device management

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
                    logging.error(f"Retrying due to error: {e}, Attempt {attempt + 1} of {retries}", 
                                  extra={'correlation_id': correlation_id})
                    time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator

@retry_on_failure()
def load_model_with_retry(model_name):
    """Attempts to load the model with retries."""
    return load_whisper_model(model_name, correlation_id)

# Error handling
def handle_unexpected_error(type, value, traceback_obj):
    """Handles unexpected errors by logging them and generating a crash report."""
    logging.critical(f"Unexpected error: {value}", exc_info=(type, value, traceback_obj), extra={'correlation_id': correlation_id})
    # Generate crash report
    crash_report = f"Exception Type: {type}\nException Value: {value}\n"
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
    response = tk.messagebox.askyesno("Unexpected Error", f"An unexpected error occurred: {value}\nA crash report has been saved to {crash_report_file}.\nWould you like to view the crash report?")
    if response:
        try:
            if sys.platform.startswith('win'):
                os.startfile(crash_report_file)
            elif sys.platform.startswith('darwin'):
                subprocess.call(('open', crash_report_file))
            else:
                subprocess.call(('xdg-open', crash_report_file))
        except Exception as e:
            logging.error(f"Failed to open crash report: {e}", extra={'correlation_id': correlation_id}, exc_info=True)

# Hook into the system's exception handler
sys.excepthook = handle_unexpected_error

def check_dependencies():
    """Checks if all required dependencies are available."""
    try:
        # Check if audio input device is available
        devices = sd.query_devices()
        if not devices:
            raise AudioProcessingError("No audio devices found.")
        default_input = sd.default.device[0]
        if default_input is None:
            raise AudioProcessingError("No default audio input device set.")
        logging.info("Audio input device is available.", extra={'correlation_id': correlation_id})
    except Exception as e:
        logging.error(f"Dependency check failed: {e}", extra={'correlation_id': correlation_id}, exc_info=True)
        tk.messagebox.showerror("Dependency Error", f"Audio input device not available: {e}")
        graceful_shutdown()

def audio_callback(indata, frames, time_info, status, gui):
    """Callback function to capture audio data."""
    try:
        if gui.is_recording:
            with lock:
                audio_buffer.append(indata.copy())
            logging.debug(f"Captured {len(indata)} frames of audio.", extra={'correlation_id': correlation_id})
    except Exception as e:
        logging.error(f"Error in audio callback: {e}", extra={'correlation_id': correlation_id}, exc_info=True)
        gui.update_status("Error")
        tk.messagebox.showerror("Error", f"Error during audio capture: {e}")

def start_recording(gui, config):
    """Starts recording audio."""
    if not config.get('record_audio', True):
        logging.info("Audio recording is disabled via configuration.", extra={'correlation_id': correlation_id})
        return
    play_start_sound()
    with lock:
        if not gui.is_recording:
            gui.is_recording = True
            audio_buffer.clear()
            gui.update_status("Recording")
            logging.info("Recording started.", extra={'correlation_id': correlation_id})
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
            logging.info("Recording stopped. Starting transcription.", extra={'correlation_id': correlation_id})
            if audio_buffer:
                audio_data = np.concatenate(audio_buffer, axis=0).flatten()
                transcription_thread = threading.Thread(target=transcribe_audio, args=(audio_data, gui), daemon=True)
                transcription_thread.start()
            else:
                logging.warning("No audio data captured.", extra={'correlation_id': correlation_id})
                gui.update_status("Idle")
            audio_buffer.clear()

def transcribe_audio(audio_data, gui):
    """Transcribes the audio data and updates the GUI."""
    try:
        gui.start_progress()
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)
        # Apply noise reduction
        noise_reduction_enabled = config.get('enable_noise_reduction', True)
        if noise_reduction_enabled:
            logging.info("Applying noise reduction...", extra={'correlation_id': correlation_id})
            # Estimate noise from the first 0.5 seconds
            noise_sample = audio_data[:int(0.5 * config.get('samplerate', 16000))]
            audio_data = nr.reduce_noise(y=audio_data, sr=config.get('samplerate', 16000), y_noise=noise_sample)
        
        # Move audio data to the same device as the model
        model_device = gui.model.device
        audio_tensor = torch.from_numpy(audio_data).to(model_device)
        
        # Perform transcription
        result = gui.model.transcribe(audio_tensor, fp16=config.get('use_fp16', False))
        transcription = result['text'].strip()
        logging.info(f"Transcription: {transcription}", extra={'correlation_id': correlation_id})
        if transcription:
            gui.append_transcription(transcription)
            if config.get('save_transcription', False):
                save_transcription(transcription, config)
            pyautogui.write(transcription + ' ')
        if config.get('save_audio', False):
            save_audio_clip(audio_data, config.get('save_directory', 'transcriptions'), config.get('samplerate', 16000), correlation_id)
        if config.get('enable_system_monitoring', True):
            log_system_usage()
        gui.update_status("Idle")
    except Exception as e:
        logging.error(f"Error during transcription: {e}", extra={'correlation_id': correlation_id}, exc_info=True)
        gui.update_status("Error")
        tk.messagebox.showerror("Error", f"Transcription failed: {e}")
    finally:
        gui.stop_progress()

def save_transcription(transcription, config):
    """Saves the transcription to a file with rollback on failure."""
    try:
        timestamp = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
        transcription_dir = config.get('save_directory', 'transcriptions')
        os.makedirs(transcription_dir, exist_ok=True)
        transcription_file = os.path.join(transcription_dir, f"transcription_{timestamp}.txt")
        temp_transcription_file = transcription_file + ".tmp"
        with open(temp_transcription_file, 'w', encoding='utf-8') as f:
            f.write(transcription)
        os.replace(temp_transcription_file, transcription_file)
        logging.info(f"Transcription saved to {transcription_file}", extra={'correlation_id': correlation_id})
    except Exception as e:
        logging.error(f"Failed to save transcription: {e}", extra={'correlation_id': correlation_id}, exc_info=True)
        # Remove temporary file if it exists
        if os.path.exists(temp_transcription_file):
            os.remove(temp_transcription_file)
        tk.messagebox.showerror("Error", f"Failed to save transcription: {e}")

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

def log_system_usage():
    """Logs system resource usage."""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    cpu_usage = process.cpu_percent(interval=1)
    logging.info(f"Memory usage: {memory_info.rss / (1024 * 1024):.2f} MB, CPU usage: {cpu_usage:.2f}%", extra={'correlation_id': correlation_id})

def key_listener(gui, config):
    """Listens for the key combination to toggle recording."""
    keys = config.get('key_combination', ['ctrl', 'alt', 'space'])
    logging.info(f"Key listener started. Waiting for {' + '.join(keys)} to toggle recording.", extra={'correlation_id': correlation_id})
    while not should_exit:
        try:
            if all(keyboard.is_pressed(key) for key in keys):
                if not gui.is_recording:
                    start_recording(gui, config)
                else:
                    stop_recording(gui)
                while all(keyboard.is_pressed(key) for key in keys):
                    time.sleep(config.get('key_listener_sleep', 0.1))
            time.sleep(config.get('key_listener_sleep', 0.1))
        except Exception as e:
            logging.error(f"Error in key listener: {e}", extra={'correlation_id': correlation_id}, exc_info=True)
            gui.update_status("Error")
            tk.messagebox.showerror("Error", f"Key listener failed: {e}")

def graceful_shutdown():
    """Handles clean shutdown on exit."""
    global should_exit
    should_exit = True
    if 'stream' in globals():
        stream.stop()
        stream.close()
    logging.info("Application has exited gracefully.", extra={'correlation_id': correlation_id})
    sys.exit(0)

def load_model_in_thread(model_name, gui):
    """Loads the model in a separate thread."""
    def load_model():
        try:
            gui.update_status(f"Loading model '{model_name}'...")
            gui.start_progress()
            model_loaded = load_model_with_retry(model_name)
            gui.model = model_loaded
            gui.update_status(f"Model '{model_name}' loaded.")
            gui.stop_progress()
        except Exception as e:
            logging.error(f"Failed to load model '{model_name}': {e}", extra={'correlation_id': correlation_id}, exc_info=True)
            gui.stop_progress()
            # Try to load a smaller model
            fallback_models = ['base', 'small', 'tiny']
            if model_name in fallback_models:
                fallback_models.remove(model_name)
            for fallback_model in fallback_models:
                try:
                    gui.update_status(f"Loading fallback model '{fallback_model}'...")
                    gui.start_progress()
                    model_loaded = load_model_with_retry(fallback_model)
                    gui.model = model_loaded
                    gui.update_status(f"Model '{fallback_model}' loaded.")
                    gui.stop_progress()
                    tk.messagebox.showinfo("Model Load", f"Loaded fallback model '{fallback_model}' instead.")
                    return
                except Exception as e2:
                    logging.error(f"Failed to load fallback model '{fallback_model}': {e2}", extra={'correlation_id': correlation_id}, exc_info=True)
            tk.messagebox.showerror("Model Load Error", f"Failed to load model '{model_name}' and fallback models.")
            graceful_shutdown()
    threading.Thread(target=load_model, daemon=True).start()

# Main execution
if __name__ == "__main__":
    try:
        config = load_config()
    except ConfigError as e:
        tk.messagebox.showerror("Configuration Error", f"Failed to load configuration: {e}")
        sys.exit(1)
    setup_logging(config, correlation_id)
    sys.excepthook = handle_unexpected_error

    # Initialize the GUI first
    root = tk.Tk()
    gui = TranscriptionGUI(root, config, None, lambda: stop_recording(gui), correlation_id, None)

    # Start loading the model in a separate thread
    default_model_name = config.get('model_support', {}).get('default_model', 'base')
    load_model_in_thread(default_model_name, gui)

    # Check dependencies before starting
    check_dependencies()

    try:
        stream = start_audio_stream(
            callback=lambda indata, frames, time_info, status: audio_callback(indata, frames, time_info, status, gui),
            samplerate=config.get('samplerate', 16000),
            channels=config.get('channels', 1),
            dtype=config.get('dtype', 'float32')
        )
    except AudioProcessingError as e:
        logging.error(f"Failed to start audio input stream: {e}", extra={'correlation_id': correlation_id}, exc_info=True)
        tk.messagebox.showerror("Error", f"Failed to start audio input stream: {e}")
        graceful_shutdown()

    listener_thread = threading.Thread(target=key_listener, args=(gui, config), daemon=True)
    listener_thread.start()

    if config.get('enable_system_monitoring', True):
        system_monitor_thread = threading.Thread(target=log_system_usage, daemon=True)
        system_monitor_thread.start()

    gui.exit_button.config(command=graceful_shutdown)
    root.mainloop()
