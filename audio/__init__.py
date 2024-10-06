# audio/__init__.py

from .streaming import start_audio_stream
from .saving import save_audio_clip
from .error import AudioProcessingError
from .notifications import notify_user

__all__ = [
    'start_audio_stream',
    'save_audio_clip',
    'AudioProcessingError',
    'notify_user'
]
