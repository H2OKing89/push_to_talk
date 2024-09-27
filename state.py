# state.py
import threading
import uuid

# Lock for synchronizing access to shared resources
lock = threading.Lock()

# Flag to signal threads to exit
should_exit = False

# Shared audio buffer
audio_buffer = []

# Unique correlation ID for the session
correlation_id = str(uuid.uuid4())
