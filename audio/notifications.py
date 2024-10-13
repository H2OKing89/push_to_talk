# audio/notifications.py

import logging
from utils import sanitize_message
from tkinter import messagebox

# Set up module-specific logger
logger = logging.getLogger(__name__)

def notify_user(gui, title: str, message: str, level: str = "info"):
    """
    Sends a notification to the user via the GUI.

    Args:
        gui: The GUI instance.
        title (str): Title of the notification.
        message (str): Message content.
        level (str): Level of the notification ('info', 'warning', 'error').
    """
    sanitized_message_content = sanitize_message(message)
    logger.debug(f"Preparing to notify user: {title} - {sanitized_message_content}")
    
    def show_message():
        if level == "info":
            messagebox.showinfo(title, message)
        elif level == "warning":
            messagebox.showwarning(title, message)
        elif level == "error":
            messagebox.showerror(title, message)
        else:
            logger.warning(f"Unknown notification level: {level}")

    if gui:
        gui.root.after(0, show_message)
    else:
        logger.error("GUI instance is None. Cannot send notification.")
