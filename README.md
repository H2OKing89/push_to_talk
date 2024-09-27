# README.md
# Push-to-Talk Transcription Application

## Overview
A Python-based application that allows users to record audio using a push-to-talk mechanism, transcribe the audio using Whisper models, and manage configurations through a user-friendly GUI.

## Features
- **Push-to-Talk Recording:** Start and stop recording using customizable key combinations.
- **Audio Transcription:** Transcribe recorded audio using various Whisper models.
- **Configurable Preferences:** Adjust settings such as key combinations, transcription and audio saving, recording duration, and more via the GUI.
- **Live Waveform Visualization:** Visualize audio input in real-time.
- **System Monitoring:** Log system resource usage.
- **Always on Top:** Keep the application window above others.

## Installation

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/yourusername/push_to_talk.git
    cd push_to_talk
    ```

2. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

    > **Note:** 
    > - `winsound` is only available on Windows. For cross-platform sound playback, consider using alternatives like `beepy` or `pygame`.
    > - The `keyboard` library may require administrative privileges on some operating systems. Ensure you run the script with the necessary permissions.

3. **Configuration:**
    - Modify the `config.yaml` file to adjust default settings or use the Preferences window in the application to make changes.

## Usage

Run the application using:
```bash
python main.py
