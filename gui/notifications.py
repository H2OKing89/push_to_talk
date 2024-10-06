# gui/notifications.py

from plyer import notification  # For system notifications
import logging
from utils.logging_utils import sanitize_message  # Corrected import

logger = logging.getLogger(__name__)

def send_system_notification(title: str, message: str):
    """Sends a system notification."""
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="Push-to-Talk Transcription",
            timeout=5
        )
    except Exception as e:
        logger.error(f"Failed to send system notification: {sanitize_message(str(e))}", exc_info=True)
