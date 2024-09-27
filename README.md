Sure! Here's the updated `README.md` for your **Push-to-Talk Transcription Application** with your Discord link instead of an email.

---

# Push-to-Talk Transcription Application

## Overview

The **Push-to-Talk Transcription Application** is a desktop application that captures real-time audio input, transcribes the audio using OpenAI's Whisper model, and provides live feedback through a graphical user interface (GUI). It is designed to be simple yet powerful, allowing users to configure settings such as transcription models, keybindings for push-to-talk functionality, audio recording preferences, and more.

The application includes real-time waveform visualization, transcription saving, audio logging, and various customization options. It uses machine learning models for transcription and includes a comprehensive logging system for debugging and performance monitoring.

---

## Features

- **Push-to-Talk functionality:** Use custom key combinations to control when audio is recorded.
- **Whisper-based Transcription:** Real-time transcription using the OpenAI Whisper model.
- **Live Waveform Visualization:** Visualize your audio input in real-time with customizable settings.
- **Configurable Key Combinations:** Customize the key combination that triggers recording.
- **System Monitoring:** Optional logging of system usage (CPU, memory) during transcription.
- **Preferences Management:** Easily modify app preferences like default transcription models and log levels.
- **Error Logging:** Comprehensive error handling and logging system with customizable log retention policies.
- **Cross-platform Compatibility:** Supports Windows and Linux systems (with minor adjustments for audio).

---

## Installation

### 1. Prerequisites

- **Python 3.8+**
- **pip** (Python package manager)
- **FFmpeg** (for processing audio)
- **OpenAI Whisper Model**

### 2. Installing Dependencies

You can install the required dependencies using the following command:

```bash
pip install -r requirements.txt
```

The `requirements.txt` should include:

```
whisper
numpy
sounddevice
soundfile
pyyaml
python-json-logger
psutil
matplotlib
tkinter
keyboard
pyautogui
```

### 3. Clone the Repository

```bash
git clone https://github.com/H2OKing89/push_to_talk.git
cd push_to_talk
```

### 4. Run the Application

```bash
python main.py
```

---

## Usage

### Key Features

1. **Key Combination for Push-to-Talk:**
   - By default, the key combination to activate recording is `Ctrl + Alt + Space`.
   - This can be customized in the `config.yml` file under the `KeyListener` section.

2. **Real-Time Transcription:**
   - The application captures audio and uses the OpenAI Whisper model to transcribe it.
   - Transcriptions appear live in the GUI.

3. **Waveform Visualization:**
   - Audio input is visualized in real-time in the `Live Audio Waveform` section.
   - The waveform plot updates dynamically based on the incoming audio stream.

4. **Saving Audio and Transcription:**
   - You can choose to save both the transcribed text and audio files. This can be toggled from the preferences menu.

---

## Configuration

### Configuration File (`config.yml`)

The configuration file controls various aspects of the application's behavior:

```yaml
KeyListener:
  key_combination:
    - ctrl
    - alt
    - space
  key_listener_sleep: 0.1  # The interval (in seconds) between key checks.

model_support:
  available_models:
    - tiny
    - base
    - small
    - medium
    - large
  default_model: base  # The default Whisper model used for transcription.

GUI:
  always_on_top: true  # Keep the application window always on top of other windows.

Logging:
  log_level: DEBUG  # Controls the logging level (e.g., DEBUG, INFO, WARNING, ERROR).
  log_to_console: true  # Log to the console as well as to the file.
  log_dir: logs/push_to_logs  # Directory where log files are stored.
  log_file: push_to_talk.log  # The name of the log file.

LogCleanup:
  cleanup_enabled: true  # Enable automatic log cleanup.
  retention_days: 7  # Retain log files for this many days.
  max_log_files: 10  # Maximum number of log files to retain.
```

### Changing Preferences In-App

You can access the **Settings > Preferences** menu to modify key settings, including:

- Whisper model selection (e.g., tiny, base, small, medium, large).
- Always-on-top functionality for the GUI.
- Key combinations for triggering audio recording.
- Logging levels (DEBUG, INFO, etc.).

After changing preferences, click "Save" to apply your changes.

---

## Logging

The application uses structured JSON logging for easy tracking of events, errors, and system usage. The logging system supports log rotation and cleanup, ensuring old logs are automatically deleted based on a time or size strategy.

Logs can be found in the specified log directory (`logs/push_to_logs/` by default).

### Example Log Entry:

```json
{
  "timestamp": "2024-09-26 23:40:08,953",
  "level": "INFO",
  "message": "Audio input stream started.",
  "correlation_id": "b23fa152-5dd6-4652-8610-ce5b157c3ded"
}
```

---

## Troubleshooting

### Common Errors

1. **KeyListener Not Responding:**
   - Ensure the key combination is correctly configured in the `config.yml`.
   - Check if any other application is intercepting the key combination.

2. **Audio Input Issues:**
   - Verify that your microphone is correctly connected and accessible by the system.
   - Check the logs for any errors related to the audio stream.

3. **Transcription Fails:**
   - Ensure that the Whisper model is correctly installed and accessible.
   - Verify your model setting in the `config.yml` and try switching to a different model if necessary.

4. **Log Cleanup Not Working:**
   - Ensure that log cleanup is enabled in the `config.yml`.
   - Check for permission issues in the log directory.

---

## Roadmap

### Future Enhancements

- **More Advanced Preferences UI:**
  - Add more settings and customization options in the preferences window.
  
- **Support for Multiple Keybindings:**
  - Allow users to set multiple key combinations for different actions (start, stop, etc.).

- **Enhanced System Monitoring:**
  - Add graphs to visualize CPU and memory usage while the application is running.

- **Transcription Languages:**
  - Add support for selecting transcription languages within the GUI.

---

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/my-feature`.
3. Commit your changes: `git commit -m 'Add new feature'`.
4. Push to the branch: `git push origin feature/my-feature`.
5. Open a pull request.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

---

## Contact

For any inquiries or support, please contact me via **Discord**:

- **Discord:** [https://discordapp.com/users/211993573204164618/](https://discordapp.com/users/211993573204164618/)

---

Let me know if this works for you, or if you'd like any further modifications!