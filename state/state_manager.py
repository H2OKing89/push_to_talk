# state/state_manager.py

import threading
import uuid

class State:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(State, cls).__new__(cls)
                    cls._instance.initialize()
        return cls._instance

    def initialize(self):
        self.lock = threading.Lock()
        self.should_exit = False  # Variable to indicate exit from key listener
        self.audio_buffer = []  # Buffer for storing captured audio
        self.correlation_id = str(uuid.uuid4())  # Unique correlation ID for logging

    def reset_correlation_id(self):
        self.correlation_id = str(uuid.uuid4())

# Instantiate the singleton
state = State()
