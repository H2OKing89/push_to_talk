# Push-to-Talk Transcription Application

## Overview

The **Push-to-Talk Transcription Application** is a desktop application that captures real-time audio input, transcribes the audio using OpenAI's Whisper model, and provides live feedback through a graphical user interface (GUI). It is designed to be simple yet powerful, allowing users to configure settings such as transcription models, keybindings for push-to-talk functionality, audio recording preferences, and more.

The application includes real-time waveform visualization, transcription saving, audio logging, and various customization options. It uses machine learning models for transcription and includes a comprehensive logging system for debugging and performance monitoring.

---

## Features

- **Push-to-Talk Functionality:** Use custom key combinations to control when audio is recorded.
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

- **Python 3.8+** (Recommended: Python 3.12)
- **pip** (Python package manager)
- **FFmpeg** (for processing audio)
- **Microsoft C++ Build Tools** (Windows only, required for some Python packages)
- **OpenAI Whisper Model**

### 2. Clone the Repository

First, clone the repository to your local machine:

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
# Audio Processing
sounddevice>=0.4.6
soundfile>=0.10.3.post1
numpy>=1.25.0

# Configuration Management
PyYAML>=6.0

# Logging
python-json-logger>=2.0.7

# GUI and Visualization
matplotlib>=3.7.1
pyautogui==0.9.54  # Adjusted to the latest available version

# System Monitoring and Control
psutil>=5.9.5
keyboard>=0.13.5

# Whisper Transcription
openai-whisper>=2023.3.14

# Optional (for enhanced tooltip functionality)
Pillow>=9.5.0
```

**Notes:**

- **`pyautogui==0.9.54`:** Specifies the exact version to avoid installation issues since `pyautogui>=0.10.1` may not be available or compatible.
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
    - If `pyautogui==0.9.54` still fails, try installing it separately:
      ```bash
      pip install pyautogui==0.9.54
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

1. **Key Combination for Push-to-Talk:**
   - By default, the key combination to activate recording is `Ctrl + Alt + Space`.
   - This can be customized in the `config.yml` file under the `KeyListener` section or through the in-app Preferences.

2. **Real-Time Transcription:**
   - The application captures audio and uses the OpenAI Whisper model to transcribe it.
   - Transcriptions appear live in the GUI.

3. **Waveform Visualization:**
   - Audio input is visualized in real-time in the `Live Audio Waveform` section.
   - The waveform plot updates dynamically based on the incoming audio stream.

4. **Saving Audio and Transcription:**
   - You can choose to save both the transcribed text and audio files. This can be toggled from the Preferences menu.

5. **System Monitoring:**
   - Optionally monitor and log system resource usage (CPU, memory) during transcription.

---

## Configuration

### Configuration File (`config.yml`)

The configuration file controls various aspects of the application's behavior. Below is an example of `config.yml` with detailed explanations.

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

AudioBuffer:
  max_duration_seconds: 300  # Maximum duration to keep in buffer (e.g., 5 minutes)
```

### Changing Preferences In-App

You can access the **Settings > Preferences** menu within the application to modify key settings, including:

- **Whisper Model Selection:** Choose between models like `tiny`, `base`, `small`, `medium`, and `large`.
- **Always-On-Top Functionality:** Keep the application window above all others.
- **Key Combinations for Triggering Audio Recording:** Customize or change the key bindings.
- **Logging Levels:** Adjust the logging level (DEBUG, INFO, etc.) based on your needs.

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
   - **Cause:** Incorrect key combination configuration or another application intercepting the key combination.
   - **Solution:**
     - Ensure the key combination is correctly set in `config.yml` or through the in-app Preferences.
     - Change the key combination to a different set to avoid conflicts with other applications.

2. **Audio Input Issues:**
   - **Cause:** Microphone not connected, incorrect audio device settings, or missing audio drivers.
   - **Solution:**
     - Verify that your microphone is correctly connected and accessible by the system.
     - Check the audio device settings in your operating system.
     - Review the logs (`logs/push_to_logs/`) for any audio-related errors.

3. **Transcription Fails:**
   - **Cause:** Whisper model not loaded correctly, insufficient system resources, or incompatible audio format.
   - **Solution:**
     - Ensure the Whisper model is correctly installed and specified in `config.yml`.
     - Switch to a different model (e.g., from `base` to `small`) in the Preferences if resource constraints are an issue.
     - Check the logs for detailed error messages.

4. **Log Cleanup Not Working:**
   - **Cause:** Log cleanup settings not enabled or permission issues in the log directory.
   - **Solution:**
     - Ensure `cleanup_enabled` is set to `true` in `config.yml`.
     - Verify that the application has the necessary permissions to modify and delete files in the log directory.

5. **Dependency Installation Issues:**
   - **Cause:** Outdated `pip`, incompatible package versions, or missing system dependencies.
   - **Solution:**
     - Ensure `pip`, `setuptools`, and `wheel` are upgraded by running:
       ```bash
       python -m pip install --upgrade pip setuptools wheel
       ```
     - Verify that `pyautogui` is set to a compatible version (`pyautogui==0.9.54`).
     - Ensure that all system dependencies like **FFmpeg** are correctly installed and accessible.

6. **Unhandled Exceptions or Application Crashes:**
   - **Cause:** Unhandled errors in the application code or incompatible dependencies.
   - **Solution:**
     - Check the logs for detailed error messages.
     - Ensure all dependencies are correctly installed and compatible with your Python version.
     - Consider reinstalling the dependencies or setting up a fresh virtual environment.

### Additional Troubleshooting Steps

- **Ensure Correct Python Version:**
  - Verify that you're using Python 3.8+ (preferably Python 3.12).
  - Check the Python version by running:
    ```bash
    python --version
    ```

- **Use a Virtual Environment:**
  - Isolate dependencies to prevent conflicts.
  - If not already using one, set up a virtual environment as described in the Installation section.

- **Check System Permissions:**
  - Ensure the application has the necessary permissions to access audio devices, write logs, and save transcriptions.

- **Update `requirements.txt`:**
  - If new dependencies are added or existing ones are updated, ensure `requirements.txt` reflects these changes.

- **Clear Pip Cache and Retry Installation:**
  - Sometimes, cached packages can cause installation issues.
  - Clear the pip cache:
    ```bash
    pip cache purge
    ```
  - Retry installing dependencies:
    ```bash
    pip install --upgrade -r requirements.txt
    ```

- **Consult Logs:**
  - Detailed logs are stored in the `logs/push_to_logs/` directory.
  - Review log files for specific error messages and stack traces.

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

## Additional Resources

- **PyAutoGUI Documentation:** [https://pyautogui.readthedocs.io/en/latest/](https://pyautogui.readthedocs.io/en/latest/)
- **Whisper by OpenAI:** [https://github.com/openai/whisper](https://github.com/openai/whisper)
- **SoundDevice Documentation:** [https://python-sounddevice.readthedocs.io/en/0.4.6/](https://python-sounddevice.readthedocs.io/en/0.4.6/)
- **SoundFile Documentation:** [https://pysoundfile.readthedocs.io/en/latest/](https://pysoundfile.readthedocs.io/en/latest/)

---

## Summary of Installation Enhancements

To help others avoid the installation issues encountered, the following steps and recommendations have been included in the updated README:

1. **Use a Virtual Environment:**
   - Isolate project dependencies to prevent conflicts with other Python projects.

2. **Upgrade `pip`, `setuptools`, and `wheel`:**
   - Ensures compatibility with the latest package specifications and reduces installation errors.

3. **Adjust `requirements.txt`:**
   - Specify compatible versions for packages like `pyautogui` to prevent installation failures.

4. **Clear Pip Cache (If Needed):**
   - Helps resolve issues caused by corrupted or outdated cached packages.

5. **Install Dependencies Separately (If Needed):**
   - Offers a way to identify specific package installation issues.

6. **Install System Dependencies:**
   - Ensures that essential tools like **FFmpeg** are correctly installed and accessible.

7. **Troubleshooting Steps:**
   - Provides actionable solutions for common installation and runtime errors.

By following these comprehensive installation and troubleshooting guidelines, users should be able to set up and run the **Push-to-Talk Transcription Application** smoothly without encountering the same issues.

