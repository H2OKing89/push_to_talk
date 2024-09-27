# preferences.py
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from config import save_config, load_config
from utils import get_absolute_path, create_tooltip  # Ensure this line is present

class PreferencesWindow:
    def __init__(self, parent, config, on_save_callback):
        self.parent = parent
        self.config = config
        self.on_save_callback = on_save_callback
        self.window = tk.Toplevel(parent)
        self.window.title("Preferences")
        self.window.geometry("500x600")
        self.window.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        """Creates widgets for the preferences window."""
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Models Tab
        models_frame = ttk.Frame(notebook)
        notebook.add(models_frame, text='Models')

        ttk.Label(models_frame, text="Available Models:", font=("Helvetica", 10)).pack(anchor='w', pady=(10, 0))
        self.available_models = self.config.get('model_support', {}).get('available_models', ['tiny', 'base', 'small', 'medium', 'large'])
        self.model_var = tk.StringVar(value=self.config.get('model_support', {}).get('default_model', 'base'))
        self.model_dropdown = ttk.Combobox(models_frame, values=self.available_models, textvariable=self.model_var, state='readonly')
        self.model_dropdown.pack(fill='x', padx=10, pady=5)
        create_tooltip(self.model_dropdown, "Select the default Whisper model for transcription.")

        # Key Listener Tab
        key_listener_frame = ttk.Frame(notebook)
        notebook.add(key_listener_frame, text='Key Listener')

        ttk.Label(key_listener_frame, text="Key Combination:", font=("Helvetica", 10)).pack(anchor='w', pady=(10, 0), padx=10)
        self.key_combination_vars = []
        self.key_combination_entries = []
        default_keys = self.config.get('key_combination', ['ctrl', 'alt', 'space'])
        for i, key in enumerate(default_keys):
            key_frame = ttk.Frame(key_listener_frame)
            key_frame.pack(fill='x', padx=10, pady=2)
            ttk.Label(key_frame, text=f"Key {i+1}:", width=8).pack(side='left')
            var = tk.StringVar(value=key)
            entry = ttk.Entry(key_frame, textvariable=var, width=15)
            entry.pack(side='left', padx=(0, 10))
            self.key_combination_vars.append(var)
            self.key_combination_entries.append(entry)
            create_tooltip(entry, f"Set key {i+1} for the key combination.")

        ttk.Label(key_listener_frame, text="Key Listener Sleep (seconds):", font=("Helvetica", 10)).pack(anchor='w', pady=(10, 0), padx=10)
        self.key_listener_sleep_var = tk.DoubleVar(value=self.config.get('key_listener_sleep', 0.1))
        self.key_listener_sleep_entry = ttk.Entry(key_listener_frame, textvariable=self.key_listener_sleep_var)
        self.key_listener_sleep_entry.pack(fill='x', padx=10, pady=5)
        create_tooltip(self.key_listener_sleep_entry, "Time to wait between key listener checks (in seconds).")

        # GUI Preferences Tab
        gui_frame = ttk.Frame(notebook)
        notebook.add(gui_frame, text='GUI')

        self.always_on_top_var = tk.BooleanVar(value=self.config.get('gui_settings', {}).get('always_on_top', True))
        self.always_on_top_cb = ttk.Checkbutton(
            gui_frame,
            text="Always on Top",
            variable=self.always_on_top_var
        )
        self.always_on_top_cb.pack(anchor='w', padx=10, pady=10)
        create_tooltip(self.always_on_top_cb, "Keep the application window above all others.")

        # Logging Settings Tab
        logging_frame = ttk.Frame(notebook)
        notebook.add(logging_frame, text='Logging')

        ttk.Label(logging_frame, text="Log Level:", font=("Helvetica", 10)).pack(anchor='w', pady=(10, 0), padx=10)
        log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        self.log_level_var = tk.StringVar(value=self.config.get('Logging', {}).get('log_level', 'DEBUG'))
        self.log_level_dropdown = ttk.Combobox(logging_frame, values=log_levels, textvariable=self.log_level_var, state='readonly')
        self.log_level_dropdown.pack(fill='x', padx=10, pady=5)
        create_tooltip(self.log_level_dropdown, "Select the logging level.")

        # Save and Cancel Buttons
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill='x', padx=10, pady=10)

        self.save_button = ttk.Button(button_frame, text="Save", command=self.save_preferences)
        self.save_button.pack(side='right', padx=5)

        self.cancel_button = ttk.Button(button_frame, text="Cancel", command=self.window.destroy)
        self.cancel_button.pack(side='right', padx=5)

    def save_preferences(self):
        """Saves the preferences to the config file."""
        # Update model settings
        selected_model = self.model_var.get()
        self.config['model_support']['default_model'] = selected_model

        # Update key listener settings
        new_keys = [var.get().strip().lower() for var in self.key_combination_vars]
        if not all(new_keys):
            messagebox.showerror("Error", "All key combination fields must be filled.")
            return
        self.config['key_combination'] = new_keys

        # Update key listener sleep
        try:
            sleep_time = float(self.key_listener_sleep_var.get())
            self.config['key_listener_sleep'] = sleep_time
        except ValueError:
            messagebox.showerror("Error", "Key Listener Sleep must be a number.")
            return

        # Update GUI settings
        self.config['gui_settings']['always_on_top'] = self.always_on_top_var.get()

        # Update logging settings
        selected_log_level = self.log_level_var.get()
        self.config['Logging']['log_level'] = selected_log_level

        try:
            save_config(self.config)
            logging.info("Preferences saved successfully.", extra={'correlation_id': self.config.get('correlation_id', 'unknown')})
            messagebox.showinfo("Preferences", "Preferences saved successfully.")
            self.on_save_callback()
            self.window.destroy()
        except Exception as e:
            logging.error(f"Failed to save preferences: {e}", extra={'correlation_id': self.config.get('correlation_id', 'unknown')}, exc_info=True)
            messagebox.showerror("Error", f"Failed to save preferences: {e}")
