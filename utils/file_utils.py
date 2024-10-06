# utils/file_utils.py

import os
import sys

def get_absolute_path(relative_path):
    """Returns the absolute path based on the main script's location."""
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle (e.g., PyInstaller)
        base_path = sys._MEIPASS  # For PyInstaller
    else:
        base_path = os.path.abspath(os.path.dirname(sys.argv[0]))
    return os.path.join(base_path, relative_path)
