# utils/logging_utils.py

import re

def sanitize_message(message: str) -> str:
    """
    Sanitizes sensitive information from log messages.

    Args:
        message (str): The original log message.

    Returns:
        str: The sanitized log message.
    """
    patterns = {
        'email': r'[\w\.-]+@[\w\.-]+',
        'credit_card': r'\b(?:\d[ -]*?){13,16}\b',
        'password': r'password\s*=\s*["\'].*?["\']',
        # Add additional patterns as needed
    }
    for key, pattern in patterns.items():
        message = re.sub(pattern, f'[REDACTED {key.upper()}]', message, flags=re.IGNORECASE)
    return message
