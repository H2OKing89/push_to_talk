# gui/main_gui.py

import tkinter as tk
from tkinter import messagebox
import logging
from gui.transcription_gui import TranscriptionGUI
from config import load_config, ConfigError
from transcription.transcriber import load_whisper_model
from audio.error import AudioProcessingError
import sys
from state import state

# Set up module-specific logger
logger = logging.getLogger(__name__)

def main():
    root = tk.Tk()
    try:
        config = load_config()
    except ConfigError as e:
        messagebox.showerror("Configuration Error", str(e))
        sys.exit(1)

    try:
        model = load_whisper_model(config.model_support.default_model)
    except Exception as e:
        messagebox.showerror("Model Load Error", str(e))
        sys.exit(1)

    # Define a callback for updating log level
    def update_log_level(new_level: str):
        logging.getLogger().setLevel(new_level)
        logger.info(f"Log level updated to {new_level}", extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id})

    # Implement the graceful shutdown function
    def gui_graceful_shutdown():
        logger.info("Graceful shutdown initiated from GUI.", extra={'correlation_id': state.correlation_id, 'trace_id': state.trace_id})
        root.destroy()

    gui = TranscriptionGUI(
        root=root,
        config=config,
        model=model,
        stop_recording_callback=None,  # Will be set within the class
        correlation_id=state.correlation_id,
        trace_id=state.trace_id,
        on_model_change_callback=None,  # Implement if needed
        graceful_shutdown_callback=gui_graceful_shutdown,  # Define this function
        set_log_level_callback=update_log_level  # Define this function
    )

    # Define a callback for updating 'Always on Top'
    def update_always_on_top(new_setting: bool):
        gui.update_always_on_top(new_setting)

    # Assign the graceful shutdown function
    gui.graceful_shutdown_callback = gui_graceful_shutdown

    # Set up the protocol for window close (graceful shutdown)
    root.protocol("WM_DELETE_WINDOW", gui.graceful_shutdown)
    root.mainloop()

if __name__ == "__main__":
    main()
