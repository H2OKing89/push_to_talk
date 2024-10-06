# gui/help_dialogs.py

import tkinter as tk
from tkinter import scrolledtext, messagebox
import logging
from utils import get_absolute_path, sanitize_message
from config import load_config
import os

logger = logging.getLogger(__name__)

def show_user_guide(parent, config):
    """Displays the user guide."""
    try:
        with open(get_absolute_path(config.get('documentation_file', 'README.md')), 'r') as file:
            content = file.read()
    except FileNotFoundError:
        content = "User guide not found."

    guide_window = tk.Toplevel(parent)
    guide_window.title("User Guide")
    guide_window.geometry("800x600")
    guide_window.resizable(True, True)
    guide_window.transient(parent)  # Ensure it appears above the main window
    guide_window.grab_set()

    guide_text = scrolledtext.ScrolledText(guide_window, wrap='word', state='normal')
    guide_text.pack(expand=True, fill='both')
    guide_text.insert(tk.END, content)
    guide_text.config(state='disabled')

def show_about():
    """Displays the About dialog."""
    about_message = (
        "Push-to-Talk Transcription Application\n"
        "Version 1.0\n"
        "Developed by OpenAI ChatGPT\n"
        "© 2024 All Rights Reserved."
    )
    messagebox.showinfo("About", about_message)
