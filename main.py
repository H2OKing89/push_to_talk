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
from transcription.transcriber import Transcriber
from gui.transcription_gui import TranscriptionGUI
from audio import (
    start_audio_stream,
    save_audio_clip,
    save_transcription,
    AudioProcessingError
)
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

class MainApplication:
    def __init__(self):
        """
        Initializes the main application, including configuration, logging, GUI, and audio streams.
        """
        # Load configuration
        try:
            self.config = load_config()
        except ConfigError as e:
            # Show error message if configuration fails to load
            root = tk.Tk()
            root.withdraw()  # Hide the root window
            messagebox.showerror("Configuration Error", f"Failed to load configuration: {e}")
            graceful_shutdown()  # Use the helper function to shutdown

        # Set up logging
        setup_logging(self.config, state.correlation_id, state.trace_id)

        # Initialize the main GUI window
        self.root = tk.Tk()
        self.gui = TranscriptionGUI(
            root=self.root,
            config=self.config,
            model=None,  # Initial model is None; will be set after loading
            stop_recording_callback=self.stop_recording,
            correlation_id=state.correlation_id,
            trace_id=state.trace_id,
            on_model_change_callback=self.on_model_change,
            graceful_shutdown_callback=self.graceful_shutdown,
            set_log_level_callback=self.set_log_level_callback  # Provide the log level callback
        )

        # Initialize Transcriber
        self.transcriber = Transcriber(config=self.config)

        # Set up exception handling
        sys.excepthook = self.handle_unexpected_error

        # Start loading the initial model
        self.schedule_model_loading()

        # Start dependency checks
        self.check_dependencies()

        # Start the audio input stream
        self.start_audio_stream()

        # Start the key listener thread
        self.listener_thread = threading.Thread(target=self.key_listener, daemon=True)
        self.listener_thread.start()

        # Start the system monitoring thread if enabled
        if self.config.enable_system_monitoring:
            self.system_monitor_thread = threading.Thread(target=self.log_system_usage, daemon=True)
            self.system_monitor_thread.start()

    def handle_unexpected_error(self, exc_type, exc_value, exc_traceback):
        """
        Handles unexpected errors by logging them and generating a crash report.

        Args:
            exc_type: Exception type.
            exc_value: Exception value.
            exc_traceback: Traceback object.
        """
        sanitized_value = sanitize_message(str(exc_value))
        logger.critical(
            f"Unexpected error: {sanitized_value}",
            exc_info=(exc_type, exc_value, exc_traceback),
            extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id}
        )

        # Generate crash report
        crash_report = f"Exception Type: {exc_type.__name__}\nException Value: {sanitized_value}\n"
        crash_report += "".join(traceback.format_tb(exc_traceback))
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
        self.graceful_shutdown()

    def schedule_model_loading(self):
        """
        Schedules the model loading after the GUI is initialized.
        """
        default_model_name = self.config.model_support.default_model
        self.load_model_in_thread(default_model_name)

    def load_model_in_thread(self, model_name):
        """
        Loads the Whisper model in a separate thread to avoid blocking the main GUI thread.

        Args:
            model_name (str): The name of the model to load.
        """
        def load_model():
            try:
                self.gui.update_status("Loading Model")
                self.gui.start_progress()  # Start progress bar
                model = self.transcriber.load_whisper_model(model_name)
                self.gui.set_model(model)
                self.gui.update_status("Idle")
                logger.info(f"Model '{model_name}' loaded successfully.", extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id})
            except Exception as e:
                sanitized_error = sanitize_message(str(e))
                logger.error(
                    f"Failed to load model '{model_name}': {sanitized_error}",
                    extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id},
                    exc_info=True
                )
                self.gui.update_status("Error")
                exception_message = str(e)
                self.root.after(0, lambda: messagebox.showerror("Model Load Error", f"Failed to load model '{model_name}'.\nError: {exception_message}"))
            finally:
                self.gui.stop_progress()  # Stop progress bar

        threading.Thread(target=load_model, daemon=True).start()

    def set_log_level_callback(self, level):
        """
        Callback function to set the log level.

        Args:
            level (str): The new log level.
        """
        set_log_level(level)

    def on_model_change(self, new_model_name):
        """
        Callback function to handle model changes.

        Args:
            new_model_name (str): The name of the new model to load.
        """
        logger.info(f"Changing model to: {new_model_name}", extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id})
        self.load_model_in_thread(new_model_name)

    def check_dependencies(self):
        """
        Checks if all required dependencies are available.
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
            self.root.after(0, lambda: self.show_dependency_error_and_shutdown(e))

    def show_dependency_error_and_shutdown(self, error):
        """
        Shows an error message for dependency failures and initiates shutdown.

        Args:
            error: The exception that occurred.
        """
        messagebox.showerror("Dependency Error", f"Audio input device not available: {error}")
        self.graceful_shutdown()

    def start_audio_stream(self):
        """
        Starts the audio input stream.
        """
        try:
            device_index = self.config.audio_device_index or sd.default.device[0]
            self.stream = start_audio_stream(
                callback=lambda indata, frames, time_info, status: self.audio_callback(indata, frames, time_info, status),
                samplerate=self.config.samplerate,
                channels=self.config.channels,
                dtype=self.config.dtype,
                device=device_index,
                gui=self.gui  # Pass the GUI instance for notifications
            )
            logger.info("Audio stream started successfully.", extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id})
        except AudioProcessingError as e:
            sanitized_error = sanitize_message(str(e))
            logger.error(
                f"Failed to start audio input stream: {sanitized_error}",
                extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id},
                exc_info=True
            )
            # Schedule the shutdown to run in the main thread
            self.root.after(0, lambda: self.show_audio_stream_error_and_shutdown(e))

    def show_audio_stream_error_and_shutdown(self, error):
        """
        Shows an error message for audio stream failures and initiates shutdown.

        Args:
            error: The exception that occurred.
        """
        messagebox.showerror("Error", f"Failed to start audio input stream: {error}")
        self.graceful_shutdown()

    def audio_callback(self, indata, frames, time_info, status):
        """
        Callback function to capture audio data.

        Args:
            indata: Input audio data.
            frames: Number of frames.
            time_info: Time information.
            status: Callback status.
        """
        try:
            if self.gui.is_recording:
                with lock:
                    audio_buffer.append(indata.copy())
                # Update the waveform visualization
                self.gui.update_waveform(indata.copy())
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
            self.gui.update_status("Error")
            messagebox.showerror("Error", f"Error during audio capture: {e}")

    def start_recording(self):
        """
        Starts recording audio.
        """
        self.play_start_sound()
        with lock:
            if not self.gui.is_recording:
                self.gui.is_recording = True
                audio_buffer.clear()
                self.gui.update_status("Recording")
                logger.info("Recording started for transcription purposes.", extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id})
                self.gui.start_timeout_timer()

    def stop_recording(self):
        """
        Stops recording and initiates transcription.
        """
        if not self.gui.is_recording:
            return
        self.play_stop_sound()
        with lock:
            if self.gui.is_recording:
                self.gui.is_recording = False
                self.gui.update_status("Transcribing")
                self.gui.stop_timeout_timer()
                logger.info("Recording stopped. Starting transcription.", extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id})
                if audio_buffer:
                    audio_data = np.concatenate(audio_buffer, axis=0).flatten()
                    transcription_thread = threading.Thread(target=self.transcribe_audio, args=(audio_data,), daemon=True)
                    transcription_thread.start()
                else:
                    logger.warning("No audio data captured.", extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id})
                    self.gui.update_status("Idle")
                audio_buffer.clear()

    def transcribe_audio(self, audio_data):
        """
        Transcribes the audio data and updates the GUI.

        Args:
            audio_data: Captured audio data.
        """
        try:
            self.gui.start_progress()
            self.gui.update_status("Transcribing")

            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            noise_reduction_enabled = self.config.enable_noise_reduction
            if noise_reduction_enabled:
                logger.info("Applying noise reduction...", extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id})
                noise_sample = audio_data[:int(0.5 * self.config.samplerate)]
                audio_data = nr.reduce_noise(y=audio_data, sr=self.config.samplerate, y_noise=noise_sample)
            model_device = self.gui.model.device
            audio_tensor = torch.from_numpy(audio_data).to(model_device)
            # Perform transcription
            result = self.gui.model.transcribe(audio_tensor, fp16=self.config.use_fp16)
            transcription = result['text'].strip()
            logger.info(f"Transcription: {transcription}", extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id})
            if transcription:
                self.gui.append_transcription(transcription)
                if self.config.save_transcription:
                    save_transcription(transcription, self.config.save_directory, state.correlation_id, self.gui)
                # Simulate typing the transcription
                pyautogui.write(transcription + ' ')
            if self.config.save_audio:
                save_audio_clip(audio_data, self.config.save_directory, self.config.samplerate, state.correlation_id, self.gui)
            # Log system usage once, without blocking
            if self.config.enable_system_monitoring:
                process = psutil.Process(os.getpid())
                memory_info = process.memory_info()
                cpu_usage = process.cpu_percent(interval=0.1)
                logger.info(
                    f"Memory usage after transcription: {memory_info.rss / (1024 * 1024):.2f} MB, CPU usage: {cpu_usage:.2f}%",
                    extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id}
                )
            self.gui.update_status("Idle")
        except Exception as e:
            sanitized_error = sanitize_message(str(e))
            logger.error(
                f"Error during transcription: {sanitized_error}",
                extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id},
                exc_info=True
            )
            self.gui.update_status("Error")
            messagebox.showerror("Error", f"Transcription failed: {e}")
        finally:
            # Clear the audio buffer to delete temporary audio data
            with lock:
                audio_buffer.clear()
            self.gui.stop_progress()

    def key_listener(self):
        """
        Listens for the key combination to toggle recording.
        """
        keys = self.config.key_combination
        logger.info(
            f"Key listener started. Waiting for {' + '.join(keys)} to toggle recording.",
            extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id}
        )
        while not should_exit:
            try:
                if all(keyboard.is_pressed(key) for key in keys):
                    if not self.gui.is_recording:
                        self.root.after(0, self.start_recording)
                    else:
                        self.root.after(0, self.stop_recording)
                    # Wait until the keys are released to prevent multiple toggles
                    while all(keyboard.is_pressed(key) for key in keys):
                        time.sleep(self.config.key_listener_sleep)
                time.sleep(self.config.key_listener_sleep)
            except Exception as e:
                sanitized_error = sanitize_message(str(e))
                logger.error(
                    f"Error in key listener: {sanitized_error}",
                    extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id},
                    exc_info=True
                )
                self.gui.update_status("Error")
                messagebox.showerror("Error", f"Key listener failed: {e}")

    def log_system_usage(self):
        """
        Logs system resource usage periodically.
        """
        while not should_exit:
            try:
                process = psutil.Process(os.getpid())
                memory_info = process.memory_info()
                cpu_usage = process.cpu_percent(interval=1)
                logger.info(
                    f"Memory usage: {memory_info.rss / (1024 * 1024):.2f} MB, CPU usage: {cpu_usage:.2f}%",
                    extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id}
                )
                time.sleep(60)  # Log every 60 seconds
            except Exception as e:
                sanitized_error = sanitize_message(str(e))
                logger.error(
                    f"Error while logging system usage: {sanitized_error}",
                    extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id},
                    exc_info=True
                )
                time.sleep(60)

    def play_start_sound(self):
        """
        Plays a beep sound when recording starts.
        """
        try:
            if sys.platform.startswith('win'):
                winsound.Beep(1000, 200)  # Frequency 1000 Hz, Duration 200 ms
            else:
                # Cross-platform beep
                print('\a')
        except Exception as e:
            sanitized_error = sanitize_message(str(e))
            logger.error(
                f"Failed to play start sound: {sanitized_error}",
                extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id},
                exc_info=True
            )

    def play_stop_sound(self):
        """
        Plays a beep sound when recording stops.
        """
        try:
            if sys.platform.startswith('win'):
                winsound.Beep(600, 200)  # Frequency 600 Hz, Duration 200 ms
            else:
                # Cross-platform beep
                print('\a')
        except Exception as e:
            sanitized_error = sanitize_message(str(e))
            logger.error(
                f"Failed to play stop sound: {sanitized_error}",
                extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id},
                exc_info=True
            )

    def graceful_shutdown(self):
        """
        Gracefully shuts down the application.
        """
        global should_exit
        try:
            should_exit = True
            logger.info("Initiating graceful shutdown...", extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id})
            # Stop audio stream
            if hasattr(self, 'stream') and self.stream.active:
                self.stream.stop()
                self.stream.close()
                logger.info("Audio stream stopped.", extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id})
            # Stop GUI
            self.root.quit()
            self.root.destroy()
            logger.info("Application shutdown completed.", extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id})
            sys.exit(0)
        except Exception as e:
            sanitized_error = sanitize_message(str(e))
            logger.error(
                f"Error during graceful shutdown: {sanitized_error}",
                extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id},
                exc_info=True
            )
            sys.exit(1)

    def run(self):
        """
        Runs the main application loop.
        """
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt received. Shutting down.", extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id})
            self.graceful_shutdown()
        except Exception as e:
            self.handle_unexpected_error(*sys.exc_info())

if __name__ == "__main__":
    try:
        app = MainApplication()
        app.run()
    except Exception as e:
        # Catch any exception not caught within the application
        sanitized_error = sanitize_message(str(e))
        logger.critical(
            f"Fatal error in main execution: {sanitized_error}",
            exc_info=True,
            extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id}
        )
        graceful_shutdown()
