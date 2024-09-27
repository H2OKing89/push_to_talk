# preferences.py
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from config import save_config

class PreferencesWindow:
    def __init__(self, parent, config, on_save_callback):
        self.parent = parent
        self.config = config
        self.on_save_callback = on_save_callback
        self.window = tk.Toplevel(parent)
        self.window.title("Preferences")
        self.window.geometry("400x300")
        self.window.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        """Creates widgets for the preferences window."""
        # Example: Toggle for saving transcription
        self.transcription_var = tk.BooleanVar(value=self.config.get('save_transcription', False))
        self.transcription_cb = ttk.Checkbutton(
            self.window,
            text="Enable Transcription Saving",
            variable=self.transcription_var
        )
        self.transcription_cb.pack(pady=10, anchor='w', padx=10)

        # Example: Toggle for saving audio
        self.audio_var = tk.BooleanVar(value=self.config.get('save_audio', False))
        self.audio_cb = ttk.Checkbutton(
            self.window,
            text="Enable Audio Saving",
            variable=self.audio_var
        )
        self.audio_cb.pack(pady=10, anchor='w', padx=10)

        # Save Button
        self.save_button = ttk.Button(self.window, text="Save", command=self.save_preferences)
        self.save_button.pack(pady=20)

    def save_preferences(self):
        """Saves the preferences to the config file."""
        self.config['save_transcription'] = self.transcription_var.get()
        self.config['save_audio'] = self.audio_var.get()
        try:
            save_config(self.config)
            logging.info("Preferences saved successfully.", extra={'correlation_id': '0c13f4e5-26b1-4d64-8eea-a2fd50bed9b6'})
            messagebox.showinfo("Preferences", "Preferences saved successfully.")
            self.on_save_callback()
            self.window.destroy()
        except Exception as e:
            logging.error(f"Failed to save preferences: {e}", extra={'correlation_id': '0c13f4e5-26b1-4d64-8eea-a2fd50bed9b6'}, exc_info=True)
            messagebox.showerror("Error", f"Failed to save preferences: {e}")
