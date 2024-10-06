# utils/file_utils.py

import os
import sys

def get_absolute_path(relative_path):
    """Returns the absolute path based on the script's location."""
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle
        script_dir = os.path.dirname(sys.executable)
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, relative_path)
