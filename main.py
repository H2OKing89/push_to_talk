import tkinter as tk
import threading
import logging
from config import load_config, save_config
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
from state import lock, should_exit, audio_buffer, correlation_id

# Retry decorator to retry function on failure
def retry_on_failure(retries=3, delay=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logging.error(f"Retrying due to error: {e}, Attempt {attempt + 1} of {retries}", 
                                  extra={'correlation_id': correlation_id})
                    time.sleep(delay)
            raise e
        return wrapper
    return decorator

@retry_on_failure()
def load_model_with_retry(model_name):
    """Attempts to load the model with retries."""
    return load_whisper_model(model_name, correlation_id)

# Error handling
def handle_unexpected_error(type, value, traceback_obj):
    """Handles unexpected errors by logging them."""
    logging.critical(f"Unexpected error: {value}", exc_info=(type, value, traceback_obj), extra={'correlation_id': correlation_id})
    tk.messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {value}")

# Hook into the system's exception handler
sys.excepthook = handle_unexpected_error

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

def start_recording(gui, model, config):
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
        result = model.transcribe(audio_data, fp16=config.get('use_fp16', False))
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
    """Saves the transcription to a file."""
    try:
        timestamp = datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
        transcription_dir = config.get('save_directory', 'transcriptions')
        os.makedirs(transcription_dir, exist_ok=True)
        transcription_file = os.path.join(transcription_dir, f"transcription_{timestamp}.txt")
        with open(transcription_file, 'w', encoding='utf-8') as f:
            f.write(transcription)
        logging.info(f"Transcription saved to {transcription_file}", extra={'correlation_id': correlation_id})
    except Exception as e:
        logging.error(f"Failed to save transcription: {e}", extra={'correlation_id': correlation_id}, exc_info=True)
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
                    start_recording(gui, model, config)
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
    should_exit = True
    if 'stream' in locals():
        stream.stop()
        stream.close()
    logging.info("Application has exited gracefully.", extra={'correlation_id': correlation_id})
    sys.exit(0)

# Main execution
if __name__ == "__main__":
    config = load_config()
    setup_logging(config, correlation_id)
    sys.excepthook = handle_unexpected_error
    model = load_model_with_retry(config.get('model_support', {}).get('default_model', 'base'))

    root = tk.Tk()
    gui = TranscriptionGUI(root, config, model, lambda: stop_recording(gui), correlation_id, None)

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
