# Push-to-Talk Transcription Application

## Overview

The **Push-to-Talk Transcription Application** is a robust desktop tool designed to capture real-time audio input, transcribe the audio using OpenAI's Whisper model, and provide live feedback through an intuitive graphical user interface (GUI). Tailored for simplicity and power, it offers customizable settings for transcription models, keybindings for push-to-talk functionality, audio recording preferences, and more.

Key features include real-time waveform visualization, transcription saving, comprehensive audio logging, and a flexible logging system adhering to established standards. The application leverages machine learning models for accurate transcription and incorporates a detailed logging framework for effective debugging and performance monitoring.

---

## Features

- **Push-to-Talk Functionality:** Control audio recording using customizable key combinations.
- **Whisper-based Transcription:** Real-time transcription powered by the OpenAI Whisper model.
- **Live Waveform Visualization:** Visualize audio input in real-time with dynamic updates.
- **Configurable Key Combinations:** Customize keybindings to suit your workflow and avoid shortcut conflicts.
- **System Monitoring:** Optional logging of system resource usage (CPU, memory) during transcription.
- **Preferences Management:** Easily modify application settings like default transcription models and log levels through the GUI.
- **Comprehensive Logging:** Structured, contextual logging adhering to best practices for consistency and security.
- **Error Logging and Crash Reporting:** Detailed error handling with sanitized logs and crash reports for effective debugging.
- **Cross-Platform Compatibility:** Supports Windows and Linux systems with minor adjustments for audio configurations.

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

### 5. Update `requirements.txt`

Ensure your `requirements.txt` has compatible versions, especially for packages that may have compatibility issues with newer Python versions like Python 3.12.

**Updated `requirements.txt`:**

```plaintext
# Audio Processing Dependencies
sounddevice>=0.4.6           # For capturing audio input from the microphone
soundfile>=0.10.3.post1      # For reading and writing sound files
numpy>=1.25.0                # Fundamental package for scientific computing

# Configuration Management
PyYAML>=6.0                  # For parsing YAML configuration files

# Logging
python-json-logger>=2.0.7    # For structured JSON logging

# GUI and Visualization
matplotlib>=3.7.1             # For plotting audio waveforms
pyautogui>=0.9.54             # For automating keyboard inputs

# System Monitoring and Control
psutil>=5.9.5                 # For accessing system details and process utilities
keyboard>=0.13.5              # For capturing global keyboard events

# Whisper Transcription
openai-whisper>=2023.3.14     # OpenAI's Whisper model for transcription

# Optional Dependencies
Pillow>=9.5.0                 # For enhanced tooltip functionality in the GUI

# Noise Reduction
noisereduce>=1.0.0            # For reducing background noise in audio clips

# PyTorch (for GPU acceleration)
torch>=2.0.0                  # PyTorch for deep learning. Install the appropriate CUDA version based on your system.
```

**Notes:**

- **`pyautogui>=0.9.54`:** Allows for minor updates and bug fixes while maintaining compatibility.
- **Version Specifiers (`>=` and `==`):** Use `>=` for flexibility and `==` for exact versions where necessary.

### 6. Install Dependencies

With the virtual environment activated and `requirements.txt` updated, install the required packages:

```bash
pip install --upgrade -r requirements.txt
```

**Troubleshooting Tips:**

- **`pyautogui` Installation Issues:**
  - If you encounter errors related to `pyautogui` not being found or incompatible:
    - Ensure you're using the latest version of `pip` by running `pip install --upgrade pip`.
    - If `pyautogui>=0.9.54` still fails, try installing it separately:
      ```bash
      pip install pyautogui>=0.9.54
      ```
    - On **Windows**, ensure that the **Microsoft C++ Build Tools** are installed, as some packages require compilation.
    - On **macOS/Linux**, ensure that you have the necessary permissions and dependencies, such as `python3-tk` for GUI functionalities.

- **`numpy` Installation Issues:**
  - If `numpy>=1.25.0` fails to install, verify that you're using a compatible Python version (Python 3.8+).
  - Ensure that your virtual environment is activated.
  - If problems persist, consider using Conda for managing dependencies.

### 7. Install FFmpeg

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

### 8. Run the Application

With all dependencies installed, you can now run the application:

```bash
python main.py
```

---

## Usage

### Key Features

1. **Push-to-Talk Control:**
   - Activate recording using the configured key combination (`Ctrl + Shift + Space` by default).
   - Customize keybindings via the Preferences menu or `config.yaml`.

2. **Real-Time Transcription:**
   - The application captures audio and uses the Whisper model to transcribe it in real-time.
   - Transcriptions are displayed live in the GUI and can be saved based on preferences.

3. **Waveform Visualization:**
   - Visualize audio input in real-time within the `Live Audio Waveform` section.
   - The waveform updates dynamically based on incoming audio data.

4. **Saving Transcriptions and Audio:**
   - Optionally save transcribed text and audio recordings to specified directories.
   - Toggle these settings in the Preferences menu.

5. **System Monitoring:**
   - Monitor and log system resource usage (CPU, memory) during transcription.
   - Enable or disable this feature in Preferences.

6. **Preferences Management:**
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
  default_model: small  # Default Whisper model to use for transcription. Options: tiny, base, small, medium, large.

key_combination:
  - ctrl
  - shift
  - space  # Key combination to toggle recording. Customize as needed to avoid conflicts with other shortcuts.

samplerate: 16000  # Audio sampling rate in Hz. Common values: 16000, 44100, 48000.

channels: 1  # Number of audio channels. 1 for mono, 2 for stereo.

dtype: float32  # Data type for audio samples. Options: float32, int16, etc.

gui_settings:
  always_on_top: false  # If true, keeps the application window above all others.

Logging:
  log_level: DEBUG          # Global log level. Options: DEBUG, INFO, WARNING, ERROR, CRITICAL.
  console_log_level: INFO   # Log level for console output. Helps in controlling verbosity in the terminal.
  log_to_console: false     # If true, logs will be output to the console in addition to log files.
  log_dir: logs/push_to_talk_logs  # Directory where log files are stored.
  log_format: json          # Format of the logs. Options: json (structured logging), plain (simple text).
  enable_dynamic_log_level: true  # Allows changing the log level at runtime via the GUI.

enable_noise_reduction: true  # Enables noise reduction on recorded audio to improve transcription accuracy.

max_recording_duration: 60  # Maximum duration (in seconds) for each recording session to prevent excessively long recordings.

LogCleanup:
  cleanup_enabled: true        # If true, enables automatic cleanup of old log files based on the retention policy.
  max_log_files: 10            # Maximum number of log files to retain when using the 'count' retention strategy.
  retention_days: 7            # Number of days to retain log files when using the 'time' retention strategy.
  retention_strategy: time     # Strategy for log retention. Options: 'time' (based on age), 'count' (based on number).

save_transcription: false  # If true, saves transcribed text to files in the specified directory.
save_audio: false          # If true, saves recorded audio clips to files in the specified directory.
save_directory: transcriptions  # Directory where transcriptions and audio clips are saved. Ensure this directory exists or the application has permission to create it.

enable_system_monitoring: true  # If true, logs system resource usage (CPU, Memory) periodically for monitoring purposes.

use_fp16: true  # If true, uses 16-bit floating-point precision during transcription to potentially improve performance on compatible GPUs.

documentation_file: README.md  # Path to the user guide or documentation file displayed in the application.

record_audio: true  # Enables or disables audio recording functionality within the application.

key_listener_sleep: 0.1  # Time (in seconds) the key listener thread waits between checks to detect key presses. Lower values make the listener more responsive but consume more CPU.

audio_device_index: 2  # Index of the audio input device to use for recording. Use system tools or scripts to determine the correct index for your preferred microphone.
```

### Changing Preferences In-App

Access the **Settings > Preferences** menu within the application to modify key settings, including:

- **Whisper Model Selection:** Choose between models like `tiny`, `base`, `small`, `medium`, and `large`.
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
  "timestamp": "2024-09-26 23:40:08,953",
  "level": "INFO",
  "name": "gui",
  "message": "GUI initialized successfully.",
  "correlation_id": "b23fa152-5dd6-4652-8610-ce5b157c3ded",
  "trace_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
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

```python
# Example in audio_callback

def audio_callback(indata, frames, time_info, status, gui):
    try:
        if gui.is_recording:
            with lock:
                audio_buffer.append(indata.copy())
            # Use debug level to minimize performance impact
            logger.debug(
                f"Captured {len(indata)} frames of audio.",
                extra={'correlation_id': correlation_id, 'trace_id': trace_id}
            )
    except Exception as e:
        sanitized_error = sanitize_message(str(e))
        logger.error(
            f"Error in audio callback: {sanitized_error}",
            extra={'correlation_id': correlation_id, 'trace_id': trace_id},
            exc_info=True
        )
        gui.update_status("Error")
        tk.messagebox.showerror("Error", f"Error during audio capture: {e}")
```

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

```python
import unittest
from unittest.mock import patch
import logging

class TestLogging(unittest.TestCase):
    @patch('logging.Logger.info')
    def test_logging_message(self, mock_log_info):
        logger = logging.getLogger('test_logger')
        logger.info('Test message')
        mock_log_info.assert_called_with('Test message')

if __name__ == '__main__':
    unittest.main()
```

#### 13. Documentation of Logging Configuration

Comprehensive documentation is provided within the `logger.py` module and the README to guide developers on logging practices, configurations, and conventions.

#### 14. Logging Configuration Validation

Configurations are validated upon loading to catch issues early, ensuring that invalid settings do not disrupt the logging system.

```python
def load_config():
    # Existing code...
    valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
    log_level = config.get('Logging', {}).get('log_level', 'DEBUG').upper()
    if log_level not in valid_levels:
        raise ConfigError(f"Invalid log level: {log_level}")
    # Continue with the rest of the configuration
```

#### 15. Fully Detailed Crash Reports

When unexpected errors occur, comprehensive crash reports are generated, including exception details, stack traces, and system information, aiding in effective debugging.

```python
def handle_unexpected_error(type, value, traceback_obj):
    """Handles unexpected errors by logging them and generating a crash report."""
    sanitized_value = sanitize_message(str(value))
    logger.critical(
        f"Unexpected error: {sanitized_value}",
        exc_info=(type, value, traceback_obj),
        extra={'correlation_id': correlation_id, 'trace_id': trace_id}
    )
    # Generate crash report
    crash_report = f"Exception Type: {type.__name__}\nException Value: {sanitized_value}\n"
    import traceback
    crash_report += "".join(traceback.format_tb(traceback_obj))
    # Add system info
    crash_report += "\nSystem Information:\n"
    crash_report += f"Platform: {sys.platform}\n"
    crash_report += f"Python Version: {sys.version}\n"
    # Save crash report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    crash_report_dir = os.path.abspath('crash_reports')
    os.makedirs(crash_report_dir, exist_ok=True)
    crash_report_file = os.path.join(crash_report_dir, f"crash_report_{timestamp}.txt")
    with open(crash_report_file, 'w', encoding='utf-8') as f:
        f.write(crash_report)
    # Notify the user
    response = tk.messagebox.askyesno("Unexpected Error",
                                      f"An unexpected error occurred: {sanitized_value}\n"
                                      f"A crash report has been saved to {crash_report_file}.\n"
                                      f"Would you like to view the crash report?")
    if response:
        try:
            if sys.platform.startswith('win'):
                os.startfile(crash_report_file)
            elif sys.platform.startswith('darwin'):
                subprocess.call(('open', crash_report_file))
            else:
                subprocess.call(('xdg-open', crash_report_file))
        except Exception as e:
            sanitized_error = sanitize_message(str(e))
            logger.error(f"Failed to open crash report: {sanitized_error}", exc_info=True)
```

#### 16. Threading and GUI Updates

GUI updates from background threads are handled using `root.after` to ensure thread safety and prevent runtime errors.

```python
# In gui.py

def update_status(self, status):
    """Updates the status label."""
    self.root.after(0, self._update_status, status)

def _update_status(self, status):
    self.status_label.config(text=f"Status: {status}")
    self.root.update_idletasks()
```

#### 17. Ensuring Thread Safety in Logging

While the standard logging module is thread-safe, custom handlers or filters are reviewed to prevent race conditions or shared resource conflicts.

#### 18. Consistency in Logging Calls

All logging calls use module-specific loggers (`logger.<level>`) to maintain consistency and ensure proper log segregation.

#### 19. Sanitization of Log Messages

Sensitive information is sanitized before being logged to prevent data leaks.

```python
def sanitize_message(message):
    """Sanitizes sensitive information from log messages."""
    patterns = {
        'email': r'[\w\.-]+@[\w\.-]+',
        'credit_card': r'\b(?:\d[ -]*?){13,16}\b',
        'password': r'password\s*=\s*\S+',
        # Add additional patterns as needed
    }
    for key, pattern in patterns.items():
        message = re.sub(pattern, f'[REDACTED {key.upper()}]', message, flags=re.IGNORECASE)
    return message
```

#### 20. Audio Stream Device Parameter

Functions handling audio streams accept necessary parameters to prevent runtime errors and ensure flexibility.

```python
# audio_handler.py

def start_audio_stream(callback, samplerate, channels, dtype, device=None):
    """Starts the audio input stream."""
    try:
        stream = sd.InputStream(callback=callback, samplerate=samplerate, channels=channels, dtype=dtype, device=device)
        stream.start()
        logger.info("Audio stream started successfully.", extra={'correlation_id': correlation_id, 'trace_id': trace_id})
        return stream
    except Exception as e:
        sanitized_error = sanitize_message(str(e))
        logger.error(f"Failed to start audio stream: {sanitized_error}", exc_info=True, extra={'correlation_id': correlation_id, 'trace_id': trace_id})
        raise AudioProcessingError(f"Failed to start audio stream: {e}")
```

---

## Logging Standards and Implementation

### Objectives

Our logging system is designed to meet the following objectives to ensure a reliable, consistent, and secure logging environment:

- **Consistency:** Maintain a uniform logging structure across all modules.
- **Contextual Information:** Incorporate relevant context (`correlation_id`, `trace_id`) in each log entry.
- **Error Handling:** Capture and log exceptions effectively, including stack traces and sanitized local variables.
- **Performance:** Avoid logging in high-frequency loops to prevent performance degradation.
- **Log Rotation and Cleanup:** Implement log rotation and automatic cleanup to manage disk space efficiently.
- **Configurability:** Allow dynamic adjustments to logging levels and formats via the `config.yaml` file.
- **Robustness:** Ensure the application continues to operate even if logging fails.
- **Internationalization:** Handle non-ASCII characters in logs correctly.
- **Testing:** Implement unit tests to verify logging behavior.
- **Documentation:** Provide comprehensive documentation for logging configurations and conventions.
- **Validation:** Validate logging configurations to catch issues early.
- **Crash Reporting:** Generate comprehensive crash reports for unexpected errors.
- **Thread Safety:** Ensure thread-safe logging and GUI operations.

### Implementation Details

1. **Module-Specific Loggers:** Each module creates its own logger using `logging.getLogger(__name__)`, allowing for granular control and easier debugging.

2. **Centralized Logging Configuration (`logger.py`):** All logging settings, handlers, and formatters are defined in `logger.py` to maintain consistency across modules.

3. **Structured Logging:** Logs are structured in JSON format for machine readability and ease of parsing, enhancing log analysis capabilities.

4. **Contextual Information:** Every log entry includes `correlation_id` and `trace_id` to trace operations across different components and threads.

5. **Exception Handling:** Exceptions are logged with detailed information, including stack traces and sanitized local variables, without exposing sensitive data.

6. **Performance Optimization:** Logging within high-frequency loops or callbacks is minimized or set to `DEBUG` level to prevent performance bottlenecks.

7. **Graceful Degradation:** The application gracefully handles logging failures, ensuring that logging issues do not cause application crashes.

8. **Internationalization:** Logs are encoded in UTF-8 and support non-ASCII characters, ensuring compatibility with international text.

9. **Log Rotation and Cleanup:** Log files are rotated daily, and old logs are automatically cleaned up based on retention policies defined in `config.yaml`.

10. **Configurability:** Logging settings, including log levels, formats, and retention strategies, are configurable via the `config.yaml` file, allowing flexibility without code changes.

11. **Dynamic Log Level Adjustment:** Users can adjust the logging level at runtime through the GUI, enabling on-the-fly control over logging verbosity.

12. **Testing and Validation:** Unit tests are implemented to verify logging behavior, and configuration validations are in place to catch issues early.

13. **Documentation:** Comprehensive documentation is provided within the `logger.py` module and the README, guiding developers on logging practices and configurations.

14. **Crash Reporting:** Detailed crash reports are generated for unexpected errors, including exception details, stack traces, and system information.

15. **Thread Safety:** Logging operations are designed to be thread-safe, ensuring reliable logging in multi-threaded environments.

---

## Logging Configuration and Standards

### 1. Use Module-Specific Loggers

**Rationale:** Creating module-specific loggers (`logger = logging.getLogger(__name__)`) allows for granular control over logging behavior in different parts of your application.

**Implementation:**

- In each module, create a logger at the top:

  ```python
  # Example in gui.py

  import logging
  logger = logging.getLogger(__name__)

  # Use the logger in your code
  logger.info("GUI initialized successfully.")
  ```

- **Avoid Handler Duplication:** Do not add handlers to module-specific loggers. Instead, configure handlers in the root logger (`logger.py`), and let module-specific loggers inherit them.

- **Add Context Filters to Root Logger:** Ensure that the `ContextFilter` is added to the root logger so that all loggers inherit the context.

### 2. Centralized Logging Configuration (`logger.py`)

**Rationale:** A centralized logging configuration ensures consistency and makes it easier to manage logging settings.

**Implementation:**

- **Singleton Pattern:** Ensure that `setup_logging` is called only once during the application's lifecycle to prevent reconfiguring loggers and adding duplicate handlers.

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

### 3. Structured Logging

**Rationale:** Utilizing structured logging (e.g., JSON format) makes logs machine-readable and easier to parse.

**Implementation:**

- **Field Consistency:** Ensure that all log messages include necessary fields such as `asctime`, `levelname`, `name`, `message`, `correlation_id`, and `trace_id`.

- **Unicode Handling:** Set `json_ensure_ascii=False` and `encoding='utf-8'` in handlers to handle non-ASCII characters correctly.

### 4. Contextual Information

**Rationale:** Including contextual data like `correlation_id` and `trace_id` helps trace operations across different components and threads.

**Implementation:**

- **Add Context Filter to Root Logger:** Ensure that the `ContextFilter` is added to the root logger in `logger.py`.

- **Consistent Logging:** Pass additional context using the `extra` parameter if needed, but the `ContextFilter` should automatically include `correlation_id` and `trace_id`.

### 5. Exception Handling and Logging

**Rationale:** Logging exceptions with stack traces, local variables, and function arguments provides valuable information for debugging.

**Implementation:**

- **Selective Logging of Local Variables:** When logging exceptions, include relevant local variables, excluding sensitive data.

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

- **Sanitization:** Use the `sanitize_message` function to remove or mask sensitive data before logging.

- **Avoid Performance Impact:** Be cautious of logging large amounts of data; include only what's necessary.

### 6. Avoid Logging in High-Frequency Loops

**Rationale:** Logging inside tight loops or high-frequency callbacks can degrade performance.

**Implementation:**

- **Avoid Logging in Callbacks:** Do not include logging statements in functions like `audio_callback` unless absolutely necessary.

- **Use Conditional Logging:** If needed for debugging, use conditional statements or throttling mechanisms.

- **Logging Levels:** Use `logger.debug` for such messages and ensure that the production log level is set appropriately.

### 7. Graceful Degradation of Logging

**Rationale:** Ensure the application continues to operate even if logging fails due to issues like disk space or permissions.

**Implementation:**

- **Wrap Logging Calls:** For critical logging operations, wrap the calls in try-except blocks.

  ```python
  try:
      logger.info("Starting application.")
  except Exception as log_error:
      print(f"Logging failed: {log_error}")
  ```

- **Fallback Mechanisms:** Consider logging to the console or a fallback location if file logging fails.

### 8. Handling Non-ASCII Characters

**Rationale:** Correct handling of non-ASCII characters is essential, especially if the application processes text in various languages.

**Implementation:**

- **UTF-8 Encoding:** Ensure all file handlers use `encoding='utf-8'`.

- **JSON Formatter:** Set `json_ensure_ascii=False` in the JSON formatter.

- **Compatibility:** Verify that log processing tools and any other consumers of the logs can handle UTF-8 encoded files.

### 9. Log Rotation and Cleanup

**Rationale:** Implement log rotation to prevent log files from growing indefinitely and manage disk space usage.

**Implementation:**

- **Use TimedRotatingFileHandler:** Rotate logs based on time intervals (e.g., daily) and keep a limited number of backup files.

- **Cleanup Function:** Implement `cleanup_old_logs` to remove old logs based on retention policies.

- **Permissions and Time Synchronization:**
  - Ensure the application has permissions to delete log files.
  - Verify that system time is correctly synchronized to prevent rotation issues.

### 10. Configurable Logging via YAML

**Rationale:** Using YAML files for logging configuration allows for easy adjustments without changing code.

**Implementation:**

- **Define Logging Configurations in `config.yaml`:**

  ```yaml
  Logging:
    log_level: DEBUG          # Controls the logging level (e.g., DEBUG, INFO, WARNING, ERROR).
    console_log_level: INFO   # Log level for console output.
    log_to_console: false     # Enable or disable console logging.
    log_dir: logs/push_to_talk_logs  # Directory where log files are stored.
    log_format: json          # Log format: 'json' or 'plain'.
    enable_dynamic_log_level: true  # Allows changing the log level at runtime via the GUI.

  LogCleanup:
    cleanup_enabled: true        # Enable automatic log cleanup.
    retention_days: 7            # Number of days to retain log files.
    max_log_files: 10            # Maximum number of log files to retain.
    retention_strategy: time     # Strategy for log retention: 'time' or 'count'.
  ```

### 11. Dynamic Log Level Adjustment

**Rationale:** Allow changing the log level at runtime for flexibility during debugging and normal operations.

**Implementation:**

- **Implement `set_log_level` Function in `logger.py`:**

  ```python
  def set_log_level(new_level):
      """Dynamically sets the log level."""
      logger = logging.getLogger()
      logger.setLevel(getattr(logging, new_level.upper(), logging.DEBUG))
      for handler in logger.handlers:
          handler.setLevel(getattr(logging, new_level.upper(), logging.DEBUG))
      logger.info(f"Log level dynamically changed to {new_level.upper()}")
  ```

- **Integrate with Preferences:** Allow users to change log levels through the Preferences GUI, invoking the `set_log_level` function accordingly.

### 12. Testing and Validation of Logging

**Rationale:** Implement unit tests to verify that logging behaves as expected.

**Implementation:**

- **Use `unittest` Framework:** Mock logging and assert that log messages are emitted correctly.

  ```python
  import unittest
  from unittest.mock import patch
  import logging

  class TestLogging(unittest.TestCase):
      @patch('logging.Logger.info')
      def test_logging_message(self, mock_log_info):
          logger = logging.getLogger('test_logger')
          logger.info('Test message')
          mock_log_info.assert_called_with('Test message')

  if __name__ == '__main__':
      unittest.main()
  ```

- **Test Cases to Cover:**
  - Log message formatting.
  - Inclusion of contextual information.
  - Logging at different levels.
  - Behavior when logging fails.

### 13. Documentation of Logging Configuration

**Rationale:** Documenting logging configurations and practices helps developers understand and maintain the logging system.

**Implementation:**

- **Comments in `logger.py`:** Add comprehensive comments explaining each configuration step.

- **Developer Guide:** Include a section in your project's README detailing:
  - Logging practices.
  - Configuration options.
  - Instructions for adjusting log levels and formats.

- **Maintenance:** Keep documentation updated with any code changes.

### 14. Logging Configuration Validation

**Rationale:** Validate logging configurations to prevent issues due to misconfigurations.

**Implementation:**

- **Implement Validation in `config.py`:**

  ```python
  def load_config():
      # Existing code...
      valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
      log_level = config.get('Logging', {}).get('log_level', 'DEBUG').upper()
      if log_level not in valid_levels:
          raise ConfigError(f"Invalid log level: {log_level}")
      # Continue with the rest of the configuration
  ```

- **Error Handling:** Decide how to handle invalid configurations (e.g., use defaults, prompt the user, or abort startup).

### 15. Fully Detailed Crash Reports

**Rationale:** Generating comprehensive crash reports aids in debugging unexpected errors.

**Implementation:**

- **Enhance `handle_unexpected_error` in `main.py`:**

  ```python
  def handle_unexpected_error(type, value, traceback_obj):
      """Handles unexpected errors by logging them and generating a crash report."""
      sanitized_value = sanitize_message(str(value))
      logger.critical(f"Unexpected error: {sanitized_value}", exc_info=(type, value, traceback_obj), extra={'correlation_id': correlation_id, 'trace_id': trace_id})

      # Generate crash report
      crash_report = f"Exception Type: {type.__name__}\nException Value: {sanitized_value}\n"
      crash_report += "".join(traceback.format_tb(traceback_obj))

      # Add system info
      crash_report += "\nSystem Information:\n"
      crash_report += f"Platform: {sys.platform}\n"
      crash_report += f"Python Version: {sys.version}\n"

      # Save crash report
      timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
      crash_report_dir = os.path.abspath('crash_reports')
      os.makedirs(crash_report_dir, exist_ok=True)
      crash_report_file = os.path.join(crash_report_dir, f"crash_report_{timestamp}.txt")
      with open(crash_report_file, 'w', encoding='utf-8') as f:
          f.write(crash_report)

      # Notify the user
      response = tk.messagebox.askyesno("Unexpected Error",
                                        f"An unexpected error occurred: {sanitized_value}\n"
                                        f"A crash report has been saved to {crash_report_file}.\n"
                                        f"Would you like to view the crash report?")
      if response:
          try:
              if sys.platform.startswith('win'):
                  os.startfile(crash_report_file)
              elif sys.platform.startswith('darwin'):
                  subprocess.call(('open', crash_report_file))
              else:
                  subprocess.call(('xdg-open', crash_report_file))
          except Exception as e:
              sanitized_error = sanitize_message(str(e))
              logger.error(f"Failed to open crash report: {sanitized_error}", exc_info=True, extra={'correlation_id': correlation_id, 'trace_id': trace_id})
  ```

- **Sensitive Data:** Avoid including sensitive data in crash reports.

- **User Experience:** Provide user-friendly messages and options.

### 16. Threading and GUI Updates

**Rationale:** Updating GUI elements from non-main threads can cause runtime errors.

**Implementation:**

- **Use `root.after` Method:** Schedule GUI updates from worker threads using `root.after` to ensure they run on the main thread.

  ```python
  # In gui.py

  def update_status(self, status):
      """Updates the status label."""
      self.root.after(0, self._update_status, status)

  def _update_status(self, status):
      self.status_label.config(text=f"Status: {status}")
      self.root.update_idletasks()
  ```

- **Adjust Worker Threads:** Modify background threads to use `root.after` when interacting with GUI components.

### 17. Ensuring Thread Safety in Logging

**Rationale:** While the standard logging module is thread-safe, custom handlers or filters might not be.

**Implementation:**

- **Review Custom Handlers and Filters:** Ensure they do not access shared resources without proper synchronization.

- **Use QueueHandler if Necessary:** For high-performance logging in multi-threaded applications, consider using `QueueHandler` and `QueueListener`.

  ```python
  # logger.py

  import queue
  from logging.handlers import QueueHandler, QueueListener

  def setup_logging(config, correlation_id, trace_id):
      # Existing setup code...

      # Create a logging queue
      log_queue = queue.Queue(-1)

      # Create a QueueHandler and add it to the root logger
      queue_handler = QueueHandler(log_queue)
      logger.addHandler(queue_handler)

      # Create and start the QueueListener with the file handler
      listener = QueueListener(log_queue, file_handler)
      listener.start()
  ```

### 18. Consistency in Logging Calls

**Rationale:** Consistent use of module-specific loggers ensures that logs are correctly captured and formatted.

**Implementation:**

- **Replace `logging` with `logger`:** Search the codebase for instances of `logging.<level>(...)` and replace them with `logger.<level>(...)`.

- **Define Logger in Each Module:**

  ```python
  import logging
  logger = logging.getLogger(__name__)
  ```

- **Establish Code Conventions:** Document and enforce the practice of using module-specific loggers.

### 19. Sanitization of Log Messages

**Rationale:** Prevent sensitive information from being logged.

**Implementation:**

- **Update `sanitize_message` Function:** Ensure it covers all types of sensitive data relevant to your application.

  ```python
  def sanitize_message(message):
      """Sanitizes sensitive information from log messages."""
      patterns = {
          'email': r'[\w\.-]+@[\w\.-]+',
          'credit_card': r'\b(?:\d[ -]*?){13,16}\b',
          'password': r'password\s*=\s*\S+',
          # Add additional patterns as needed
      }
      for key, pattern in patterns.items():
          message = re.sub(pattern, f'[REDACTED {key.upper()}]', message, flags=re.IGNORECASE)
      return message
  ```

- **Consistent Use:** Apply `sanitize_message` to all logging calls that include user-generated content or exception messages.

### 20. Audio Stream Device Parameter

**Rationale:** Ensure that functions accept all necessary parameters to prevent runtime errors.

**Implementation:**

- **Update `start_audio_stream` in `audio_handler.py`:**

  ```python
  # audio_handler.py

  def start_audio_stream(callback, samplerate, channels, dtype, device=None):
      """Starts the audio input stream."""
      try:
          stream = sd.InputStream(callback=callback, samplerate=samplerate, channels=channels, dtype=dtype, device=device)
          stream.start()
          logger.info("Audio stream started successfully.", extra={'correlation_id': correlation_id, 'trace_id': trace_id})
          return stream
      except Exception as e:
          sanitized_error = sanitize_message(str(e))
          logger.error(f"Failed to start audio stream: {sanitized_error}", exc_info=True, extra={'correlation_id': correlation_id, 'trace_id': trace_id})
          raise AudioProcessingError(f"Failed to start audio stream: {e}")
  ```

- **Ensure Function Calls Include `device` Parameter:** When calling `start_audio_stream`, include the `device` parameter if needed.

---

## Logging Standards and Implementation

Our application adheres to comprehensive logging standards to ensure reliability, consistency, and security. Below are the key components and best practices implemented:

### 1. Consistency

- **Uniform Structure:** All log messages follow a consistent format, whether in JSON or plain text.
- **Module-Specific Loggers:** Each module utilizes its own logger, promoting clarity and ease of debugging.

### 2. Contextual Information

- **Correlation and Trace IDs:** Every log entry includes `correlation_id` and `trace_id` to trace operations across different components and threads.

### 3. Error Handling

- **Detailed Exception Logging:** Exceptions are logged with stack traces and sanitized local variables to aid in debugging without exposing sensitive information.
- **Graceful Degradation:** The application continues to function even if logging fails, ensuring robustness.

### 4. Performance Optimization

- **Avoid High-Frequency Logging:** Logging statements are minimized within high-frequency loops or callbacks to prevent performance degradation.
- **Debug Level Logging:** Use `logger.debug` for verbose logging in less critical parts of the code.

### 5. Log Rotation and Cleanup

- **Timed Rotation:** Logs are rotated daily using `TimedRotatingFileHandler`.
- **Automatic Cleanup:** Old log files are automatically deleted based on retention policies defined in `config.yaml`.

### 6. Configurability

- **YAML-Based Configuration:** Logging settings, including levels, formats, and retention strategies, are configurable via the `config.yaml` file.
- **Dynamic Log Level Adjustment:** Users can adjust log levels at runtime through the application's Preferences GUI.

### 7. Robustness

- **Thread-Safe Logging:** The logging system is designed to be thread-safe, preventing race conditions in multi-threaded environments.
- **Crash Reporting:** Comprehensive crash reports are generated for unexpected errors, aiding in effective debugging.

### 8. Internationalization

- **UTF-8 Encoding:** Logs handle non-ASCII characters correctly by using UTF-8 encoding.
- **JSON Formatter:** Structured logging supports international characters seamlessly.

### 9. Testing and Validation

- **Unit Tests:** Implemented unit tests verify that logging behaves as expected across different scenarios.
- **Configuration Validation:** Logging configurations are validated upon loading to catch misconfigurations early.

### 10. Documentation

- **Comprehensive Documentation:** Detailed documentation is provided within the codebase and the README, guiding developers on logging practices and configurations.
- **Comments:** In-line comments explain the purpose and usage of logging configurations and functions.

---

## Roadmap

### Future Enhancements

1. **Automatic Language Detection:**
   - Implement a feature to automatically detect the spoken language and switch to the corresponding Whisper model, enhancing multilingual support.

2. **Voice Activity Detection (VAD):**
   - Add a voice activity detection (VAD) mechanism to start and stop recording automatically based on whether the user is speaking.

3. **Noise Reduction or Cancellation:**
   - Add real-time noise reduction/cancellation to clean up background noise during recording, improving transcription accuracy.

4. **Batch Processing Mode:**
   - Enable a mode where users can upload multiple pre-recorded audio files for batch transcription processing, instead of live recording only.

5. **Advanced Preferences for Transcription Output:**
   - Allow users to customize the transcription output format (e.g., with timestamps, speaker labels, punctuation handling) through the preferences panel.

6. **Cloud Sync for Transcriptions:**
   - Implement cloud syncing or integration with services like Google Drive, Dropbox, or OneDrive to automatically back up transcriptions.

7. **Speech-to-Text Customization:**
   - Allow users to fine-tune Whisper models based on custom vocabulary or frequently used terms, improving accuracy in domain-specific jargon.

8. **Real-Time Translation:**
   - Add a translation feature that not only transcribes speech but also translates it in real-time using an external translation service (e.g., Google Translate API).

9. **Mobile App Version:**
   - Develop a companion mobile app (either iOS/Android) that works alongside the desktop app for remote control and transcription on the go.

10. **Enhanced Waveform Visualization:**
    - Add more advanced waveform features in the GUI, such as zoom, real-time frequency analysis, or annotations for key moments (e.g., when the user starts or stops speaking).

11. **Speaker Identification:**
    - Implement a speaker identification feature that recognizes multiple speakers in a conversation, helping to differentiate who is talking in the transcription.

12. **Speech Speed Control:**
    - Add functionality to adjust the speed of the transcription output, allowing for faster or slower speech depending on user preferences.

13. **Custom Shortcut Editor:**
    - Give users more control over keyboard shortcuts, allowing them to define their own key combinations for recording, playback, and other key features.

14. **Audio Effects Processing:**
    - Implement an audio effects panel in the GUI where users can apply effects like compression, equalization, or reverb to the recorded audio before saving or transcribing.

15. **Browser Extension for Transcription:**
    - Create a browser extension that allows users to transcribe audio or video directly from their browser, such as for YouTube videos or web conferences.

---

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. **Fork the Repository:**
   - Click the "Fork" button at the top right of the repository page.

2. **Create a New Branch:**
   - ```bash
     git checkout -b feature/my-feature
     ```

3. **Commit Your Changes:**
   - ```bash
     git commit -m 'Add new feature'
     ```

4. **Push to the Branch:**
   - ```bash
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

---

## Summary of Logging Implementation

Our application implements a comprehensive logging system based on the following standards to ensure reliability, consistency, and security:

1. **Module-Specific Loggers:** Each module uses its own logger, enabling granular control over logging outputs and behaviors.

2. **Centralized Logging Configuration:** All logging settings, including handlers and formatters, are defined centrally in `logger.py` to maintain consistency.

3. **Structured Logging:** Logs are structured in JSON format for machine readability and ease of parsing.

4. **Contextual Information:** Each log entry includes `correlation_id` and `trace_id` to trace operations across different components and threads.

5. **Exception Handling:** Exceptions are logged with detailed information, including stack traces and sanitized local variables, without exposing sensitive data.

6. **Performance Optimization:** Logging within high-frequency loops or callbacks is minimized to prevent performance degradation.

7. **Graceful Degradation:** The application continues to function even if logging fails, ensuring robustness.

8. **Internationalization:** Logs handle non-ASCII characters correctly by using UTF-8 encoding.

9. **Log Rotation and Cleanup:** Logs are rotated daily, and old logs are automatically cleaned up based on retention policies defined in `config.yaml`.

10. **Configurability:** Logging levels, formats, and retention strategies are configurable via the `config.yaml` file.

11. **Dynamic Log Level Adjustment:** Users can adjust log levels at runtime through the GUI, providing flexibility during debugging and normal operations.

12. **Testing and Validation:** Unit tests verify logging behavior, and configuration validations catch issues early.

13. **Documentation:** Comprehensive documentation guides developers on logging practices and configurations.

14. **Crash Reporting:** Detailed crash reports are generated for unexpected errors, aiding in effective debugging.

15. **Thread Safety:** Logging operations are thread-safe, ensuring reliable logging in multi-threaded environments.

By adhering to these logging standards, our application ensures that logs are informative, secure, and maintainable, facilitating effective debugging and monitoring.

---