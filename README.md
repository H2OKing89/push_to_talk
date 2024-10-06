# Push-to-Talk Transcription Application

## Overview

The **Push-to-Talk Transcription Application** is a robust desktop tool designed to capture real-time audio input, transcribe the audio using OpenAI's Whisper model, and provide live feedback through an intuitive graphical user interface (GUI). Tailored for simplicity and power, it offers customizable settings for transcription models, keybindings for push-to-talk functionality, audio recording preferences, and more.

Key features include real-time waveform visualization, transcription saving, comprehensive audio logging, and a flexible logging system adhering to established standards. The application leverages machine learning models for accurate transcription and incorporates a detailed logging framework for effective debugging and performance monitoring.

---

## Features

- **Push-to-Talk Functionality:** Control audio recording using customizable key combinations.
- **Whisper-based Transcription:** Real-time transcription powered by the OpenAI Whisper model, including support for the latest models like `turbo`.
- **Live Waveform Visualization:** Visualize audio input in real-time with dynamic updates using `matplotlib`.
- **Dynamic Status Updates and Recording Indicators:** Displays color-coded status messages and recording indicators for clear user feedback.
- **Configurable Key Combinations:** Customize keybindings to suit your workflow and avoid shortcut conflicts.
- **System Monitoring:** Optional logging of system resource usage (CPU, memory) during transcription.
- **Preferences Management:** Easily modify application settings like default transcription models and log levels through the GUI.
- **Comprehensive Logging:** Structured, contextual logging adhering to best practices for consistency and security.
- **Error Logging and Crash Reporting:** Detailed error handling with sanitized logs and crash reports for effective debugging.
- **Cross-Platform Compatibility:** Supports Windows, macOS, and Linux systems with minor adjustments for audio configurations.
- **Security Enhancements:** Ensures safe model loading by addressing potential security risks (e.g., `weights_only=True` when loading models).
- **Optimized Variable Access:** Global configuration access throughout the application for consistency and ease of maintenance.

---

## Installation

### 1. Prerequisites

Ensure your system meets the following requirements:

- **Python 3.8+** (Recommended: Python 3.12)
- **pip** (Python package manager)
- **FFmpeg** (for processing audio)
- **Microsoft C++ Build Tools** (Windows only, required for some Python packages)
- **OpenAI Whisper Model**

### 2. Clone the Repository

Clone the repository to your local machine:

```bash
git clone https://github.com/H2OKing89/push_to_talk.git
cd push_to_talk
```

### 3. Set Up a Virtual Environment (Recommended)

Using a virtual environment ensures that project dependencies are isolated from your global Python installation.

1. **Create a Virtual Environment:**

   ```bash
   python -m venv venv
   ```

2. **Activate the Virtual Environment:**

   - **Windows:**

     ```bash
     venv\Scripts\activate
     ```

   - **macOS/Linux:**

     ```bash
     source venv/bin/activate
     ```

### 4. Upgrade `pip`, `setuptools`, and `wheel`

Before installing dependencies, ensure that your package managers are up-to-date to handle the latest package specifications and compatibility requirements.

```bash
python -m pip install --upgrade pip setuptools wheel
```

### 5. Install Dependencies

With the virtual environment activated, install the required packages using the `requirements.txt` file.

**Updated `requirements.txt`:**

```plaintext
# Audio Processing Dependencies
sounddevice>=0.4.6           # For capturing audio input from the microphone
soundfile>=0.10.3.post1      # For reading and writing sound files
numpy>=1.25.0                # Fundamental package for scientific computing
scipy>=1.9.0                 # Additional tools for scientific computing and audio processing

# Configuration Management
PyYAML>=6.0                  # For parsing YAML configuration files

# Logging
python-json-logger>=2.0.7    # For structured JSON logging

# GUI and Visualization
matplotlib>=3.7.1            # For plotting audio waveforms
pyautogui>=0.9.54            # For automating keyboard inputs

# System Monitoring and Control
psutil>=5.9.5                # For accessing system details and process utilities
keyboard>=0.13.5             # For capturing global keyboard events

# Whisper Transcription
openai-whisper>=20240930     # OpenAI's Whisper model for transcription
torch>=2.0.0                 # PyTorch for deep learning. Install the appropriate CUDA version based on your system
torchvision>=0.15.0          # For additional vision utilities with PyTorch
tiktoken>=0.3.3              # Tokenizer for OpenAI models
tqdm>=4.64.0                 # Progress bar library used by openai-whisper
more-itertools>=9.1.0        # Additional utilities for working with iterators

# Optional Dependencies
Pillow>=9.5.0                # For enhanced tooltip functionality in the GUI

# Noise Reduction
noisereduce>=1.0.0           # For reducing background noise in audio clips
```

**Notes:**

- **Ensure Compatibility:** The versions specified are compatible with the latest features, including the `turbo` model.
- **Version Specifiers (`>=`):** Allows for minor updates and bug fixes while maintaining compatibility.

**Install Dependencies:**

```bash
pip install --upgrade -r requirements.txt
```

**Troubleshooting Tips:**

- **`pyautogui` Installation Issues:**
  - Ensure you're using the latest version of `pip` by running `pip install --upgrade pip`.
  - On **Windows**, make sure the **Microsoft C++ Build Tools** are installed.
  - On **macOS/Linux**, you might need to install additional dependencies like `python3-tk`.

- **`numpy` or `torch` Installation Issues:**
  - Verify that you're using a compatible Python version (Python 3.8+).
  - If problems persist, consider installing `torch` separately, ensuring you select the correct CUDA version for your system.

### 6. Install FFmpeg

The Whisper model relies on FFmpeg for audio processing. Ensure FFmpeg is installed and accessible in your system's PATH.

- **Windows:**
  1. Download the latest static build from [FFmpeg's official website](https://ffmpeg.org/download.html).
  2. Extract the files and add the `bin` directory to your system's PATH.

- **macOS:**

  ```bash
  brew install ffmpeg
  ```

- **Linux (Debian-based):**

  ```bash
  sudo apt-get update
  sudo apt-get install ffmpeg
  ```

**Verify Installation:**

```bash
ffmpeg -version
```

### 7. Run the Application

With all dependencies installed, you can now run the application:

```bash
python main.py
```

---

## Usage

### Key Features

1. **Push-to-Talk Control:**
   - Activate recording using the configured key combination (`Ctrl + Alt + Space` by default).
   - Customize keybindings via the Preferences menu or `config.yaml`.

2. **Real-Time Transcription:**
   - The application captures audio and uses the Whisper model to transcribe it in real-time.
   - Transcriptions are displayed live in the GUI and can be saved based on preferences.

3. **Waveform Visualization:**
   - Visualize audio input in real-time within the `Live Audio Waveform` section.
   - The waveform updates dynamically based on incoming audio data.

4. **Dynamic Status Updates and Recording Indicators:**
   - Status messages are color-coded for better user experience:
     - **Recording:** Red
     - **Transcribing:** Blue
     - **Idle:** Green
     - **Error:** Orange
   - A red indicator circle appears when recording is active.

5. **Saving Transcriptions and Audio:**
   - Optionally save transcribed text and audio recordings to specified directories.
   - Toggle these settings in the Preferences menu.

6. **System Monitoring:**
   - Monitor and log system resource usage (CPU, memory) during transcription.
   - Enable or disable this feature in Preferences.

7. **Preferences Management:**
   - Access the Preferences menu to modify settings like default transcription models, log levels, keybindings, and more.
   - Changes can be saved and applied without restarting the application.

---

## Configuration

### Configuration File (`config.yaml`)

The `config.yaml` file controls various aspects of the application's behavior. Below is the updated `config.yaml` with detailed explanations:

```yaml
# Configuration file for Push-to-Talk Transcription Application

model_support:
  available_models:
    - tiny
    - base
    - small
    - medium
    - large
    - turbo       # Added the 'turbo' model to the list of available models
  default_model: turbo  # Default Whisper model to use for transcription.

key_combination:
  - ctrl
  - alt
  - space  # Key combination to toggle recording.

samplerate: 16000  # Audio sampling rate in Hz.

channels: 1  # Number of audio channels.

dtype: float32  # Data type for audio samples.

gui_settings:
  always_on_top: false  # Keeps the application window above all others.

Logging:
  log_level: DEBUG          # Global log level.
  console_log_level: INFO   # Log level for console output.
  log_to_console: false     # Output logs to the console.
  log_dir: logs/push_to_talk_logs  # Directory for log files.
  log_format: json          # Format of the logs.
  enable_dynamic_log_level: true  # Allows changing the log level at runtime.

enable_noise_reduction: true  # Enables noise reduction on recorded audio.

max_recording_duration: 60  # Maximum duration for each recording session.

LogCleanup:
  cleanup_enabled: true        # Enables automatic cleanup of old log files.
  max_log_files: 10            # Maximum number of log files to retain.
  retention_days: 7            # Number of days to retain log files.
  retention_strategy: time     # Strategy for log retention.

save_transcription: false  # Saves transcribed text to files.
save_audio: false          # Saves recorded audio clips.
save_directory: transcriptions  # Directory for transcriptions and audio clips.

enable_system_monitoring: true  # Logs system resource usage.

use_fp16: true  # Uses 16-bit floating-point precision during transcription.

documentation_file: README.md  # Path to the user guide.

record_audio: true  # Enables audio recording functionality.

key_listener_sleep: 0.1  # Time the key listener thread waits between checks.

audio_device_index: null  # Index of the audio input device.
```

### Changing Preferences In-App

Access the **Settings > Preferences** menu within the application to modify key settings, including:

- **Whisper Model Selection:** Choose between models like `tiny`, `base`, `small`, `medium`, `large`, and `turbo`.
- **Always-On-Top Functionality:** Keep the application window above all others.
- **Key Combinations for Triggering Audio Recording:** Customize or change the key bindings.
- **Logging Levels:** Adjust the logging level (`DEBUG`, `INFO`, etc.) based on your needs.

After changing preferences, click "Save" to apply your changes.

---

## Logging

### Comprehensive Logging Standards

Our application adheres to a comprehensive logging standard to ensure consistency, context, and security across all modules. Below are the key aspects of our logging system:

### Objectives

- **Consistency:** Maintain a uniform logging structure throughout the application.
- **Contextual Information:** Include relevant context (e.g., `correlation_id`, `trace_id`) in logs.
- **Error Handling:** Capture and log exceptions effectively, including local variables and function arguments, while avoiding sensitive data exposure.
- **Performance:** Avoid logging in high-frequency loops to prevent performance degradation.
- **Log Rotation and Cleanup:** Manage log files efficiently to prevent disk space issues.
- **Configurability:** Allow dynamic adjustments to logging levels and formats via YAML configuration files.
- **Robustness:** Ensure the application continues to operate even if logging fails.
- **Internationalization:** Handle non-ASCII characters in logs correctly.
- **Testing:** Implement unit tests to verify logging behavior.
- **Documentation:** Document logging configurations and conventions for developer reference.
- **Validation:** Validate logging configurations to catch issues early.
- **Crash Reporting:** Generate comprehensive crash reports when unexpected errors occur.
- **Thread Safety:** Ensure thread-safe logging and GUI operations.

### Logging Implementation

#### 1. Module-Specific Loggers

Each module creates its own logger using `logger = logging.getLogger(__name__)`. This allows for granular control and easier debugging.

```python
# Example in gui.py

import logging
logger = logging.getLogger(__name__)

# Use the logger in your code
logger.info("GUI initialized successfully.")
```

**Note:** Do not add handlers to module-specific loggers. Handlers are configured centrally in `logger.py`.

#### 2. Centralized Logging Configuration (`logger.py`)

All logging configurations, including handlers and formatters, are defined in a centralized module to ensure consistency.

- **Root Logger Configuration:**

  - **Log Level:** Set globally via `config.yaml`.
  - **Handlers:** Includes `TimedRotatingFileHandler` for file logging and `StreamHandler` for console logging (if enabled).
  - **Formatters:** Supports JSON and plain text formats based on configuration.
  - **Context Filters:** Adds `correlation_id` and `trace_id` to each log entry for contextual tracing.

- **Log Rotation and Cleanup:**

  Configured using `TimedRotatingFileHandler` with settings defined in `config.yaml` under `LogCleanup`.

```python
# logger.py

import logging
import logging.handlers
from pythonjsonlogger import jsonlogger
import os
import threading
from datetime import datetime, timedelta
import re

log_lock = threading.Lock()
_logger_initialized = False

def setup_logging(config, correlation_id, trace_id):
    global _logger_initialized
    if _logger_initialized:
        return  # Logging is already configured

    with log_lock:
        logger = logging.getLogger()
        logger.setLevel(getattr(logging, config.get('Logging', {}).get('log_level', 'DEBUG').upper(), logging.DEBUG))

        # Log directory setup
        log_dir = os.path.abspath(config.get('Logging', {}).get('log_dir', 'logs/push_to_talk_logs'))
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'app.log')

        # File Handler
        file_handler = logging.handlers.TimedRotatingFileHandler(
            log_file,
            when='midnight',
            interval=1,
            backupCount=config.get('LogCleanup', {}).get('max_log_files', 10),
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, config.get('Logging', {}).get('log_level', 'DEBUG').upper(), logging.DEBUG))

        # Formatter
        if config.get('Logging', {}).get('log_format', 'json') == 'json':
            formatter = jsonlogger.JsonFormatter(
                fmt='%(asctime)s %(levelname)s %(name)s %(message)s correlation_id=%(correlation_id)s trace_id=%(trace_id)s',
                json_ensure_ascii=False
            )
        else:
            formatter = logging.Formatter(
                fmt='%(asctime)s - %(levelname)s - %(name)s - %(message)s - CorrelationID: %(correlation_id)s - TraceID: %(trace_id)s'
            )

        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console Handler
        if config.get('Logging', {}).get('log_to_console', False):
            console_handler = logging.StreamHandler()
            console_handler.setLevel(getattr(logging, config.get('Logging', {}).get('console_log_level', 'INFO').upper(), logging.INFO))
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        # Add Context Filter
        context_filter = ContextFilter(correlation_id, trace_id)
        logger.addFilter(context_filter)

        # Clean up old logs based on retention policy
        cleanup_old_logs(log_dir, config)

        _logger_initialized = True
```

#### 3. Structured Logging

Logs are structured in JSON format for machine readability and ease of parsing. This enhances the ability to filter and analyze logs using various tools.

**Example Log Entry:**

```json
{
  "asctime": "2024-10-06 13:58:06,396",
  "name": "__main__",
  "levelname": "INFO",
  "message": "Memory usage after transcription: 1606.24 MB, CPU usage: 0.00%",
  "correlation_id": "6433fd92-5659-4365-9374-1978628d02b8",
  "trace_id": "99e76b35-fdc3-4e76-b07a-1794a545b982"
}
```

#### 4. Contextual Information

Each log entry includes `correlation_id` and `trace_id` to trace operations across different components and threads.

- **`correlation_id`:** A unique identifier for the application session, aiding in correlating logs from the same run.
- **`trace_id`:** A unique identifier for individual operations or requests, allowing for detailed tracing within a session.

#### 5. Exception Handling and Logging

Exceptions are captured and logged with detailed information, including stack traces and sanitized local variables to prevent sensitive data exposure.

```python
import sys
import traceback

try:
    # Code that may raise an exception
    pass
except Exception as e:
    exc_type, exc_value, exc_tb = sys.exc_info()
    tb_details = traceback.format_exception(exc_type, exc_value, exc_tb)
    local_vars = {k: v for k, v in locals().items() if k not in ['sensitive_data', 'password']}
    sanitized_vars = sanitize_message(str(local_vars))
    logger.error(
        f"An error occurred: {e}\nTraceback: {''.join(tb_details)}\nLocal Variables: {sanitized_vars}",
        exc_info=False  # Set to False if you're including traceback manually
    )
```

**Note:** The `sanitize_message` function ensures that sensitive information is masked before logging.

#### 6. Avoid Logging in High-Frequency Loops

To maintain application performance, logging statements are minimized within high-frequency loops or callbacks.

#### 7. Graceful Degradation of Logging

The application ensures continued operation even if logging fails, preventing logging issues from causing application crashes.

```python
try:
    logger.info("Starting application.")
except Exception as log_error:
    print(f"Logging failed: {log_error}")
```

#### 8. Handling Non-ASCII Characters

Logs are encoded in UTF-8 and structured in JSON to support internationalization and handle non-ASCII characters seamlessly.

#### 9. Log Rotation and Cleanup

Log files are rotated daily, and old logs are automatically cleaned up based on the retention strategy defined in `config.yaml`.

#### 10. Configurable Logging via YAML Configuration Files

All logging settings, including log levels, formats, and retention policies, are configurable through the `config.yaml` file, allowing for flexibility without code changes.

#### 11. Dynamic Log Level Adjustment

Users can adjust the log level at runtime through the application's GUI, providing on-the-fly control over logging verbosity.

```python
def set_log_level(new_level):
    """Dynamically sets the log level."""
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, new_level.upper(), logging.DEBUG))
    for handler in logger.handlers:
        handler.setLevel(getattr(logging, new_level.upper(), logging.DEBUG))
    logger.info(f"Log level dynamically changed to {new_level.upper()}")
```

#### 12. Testing and Validation of Logging

Unit tests are implemented to verify that logging behaves as expected, ensuring reliability and correctness.

#### 13. Documentation of Logging Configuration

Comprehensive documentation is provided within the `logger.py` module and the README to guide developers on logging practices, configurations, and conventions.

#### 14. Logging Configuration Validation

Configurations are validated upon loading to catch issues early, ensuring that invalid settings do not disrupt the logging system.

#### 15. Fully Detailed Crash Reports

When unexpected errors occur, comprehensive crash reports are generated, including exception details, stack traces, and system information, aiding in effective debugging.

---

## Roadmap

### Future Enhancements

1. **Automatic Language Detection:**
   - Implement a feature to automatically detect the spoken language and switch to the corresponding Whisper model, enhancing multilingual support.

2. **Voice Activity Detection (VAD):**
   - Add a voice activity detection mechanism to start and stop recording automatically based on whether the user is speaking.

3. **Advanced Preferences for Transcription Output:**
   - Allow users to customize the transcription output format (e.g., with timestamps, speaker labels, punctuation handling) through the preferences panel.

4. **Cloud Sync for Transcriptions:**
   - Implement cloud syncing or integration with services like Google Drive, Dropbox, or OneDrive to automatically back up transcriptions.

5. **Speech-to-Text Customization:**
   - Allow users to fine-tune Whisper models based on custom vocabulary or frequently used terms, improving accuracy in domain-specific jargon.

6. **Real-Time Translation:**
   - Add a translation feature that not only transcribes speech but also translates it in real-time using an external translation service.

7. **Enhanced Waveform Visualization:**
   - Add more advanced waveform features in the GUI, such as zoom, real-time frequency analysis, or annotations for key moments.

8. **Speaker Identification:**
   - Implement a speaker identification feature that recognizes multiple speakers in a conversation, helping to differentiate who is talking in the transcription.

9. **Custom Shortcut Editor:**
   - Give users more control over keyboard shortcuts, allowing them to define their own key combinations for recording, playback, and other key features.

10. **Mobile App Version:**
    - Develop a companion mobile app that works alongside the desktop app for remote control and transcription on the go.

---

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. **Fork the Repository:**
   - Click the "Fork" button at the top right of the repository page.

2. **Create a New Branch:**

   ```bash
   git checkout -b feature/my-feature
   ```

3. **Commit Your Changes:**

   ```bash
   git commit -m 'Add new feature'
   ```

4. **Push to the Branch:**

   ```bash
   git push origin feature/my-feature
   ```

5. **Open a Pull Request:**
   - Navigate to the original repository and open a pull request from your forked branch.

### Guidelines

- **Code Style:** Follow PEP 8 coding standards for Python.
- **Descriptive Commits:** Write clear and descriptive commit messages.
- **Testing:** Ensure that new features include appropriate unit tests.
- **Documentation:** Update the README and other documentation as needed to reflect changes.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

---

## Contact

For any inquiries or support, please contact me via **Discord**:

- **Discord:** [https://discordapp.com/users/211993573204164618/](https://discordapp.com/users/211993573204164618/)

---

## Additional Resources

- **PyAutoGUI Documentation:** [https://pyautogui.readthedocs.io/en/latest/](https://pyautogui.readthedocs.io/en/latest/)
- **Whisper by OpenAI:** [https://github.com/openai/whisper](https://github.com/openai/whisper)
- **SoundDevice Documentation:** [https://python-sounddevice.readthedocs.io/en/0.4.6/](https://python-sounddevice.readthedocs.io/en/0.4.6/)
- **SoundFile Documentation:** [https://pysoundfile.readthedocs.io/en/latest/](https://pysoundfile.readthedocs.io/en/latest/)
- **Python Logging Documentation:** [https://docs.python.org/3/library/logging.html](https://docs.python.org/3/library/logging.html)

