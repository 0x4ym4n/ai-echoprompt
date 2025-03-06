# Voice-to-Text Transcription Tool

A desktop application that provides real-time voice recording and transcription capabilities using Groq's Whisper API. The tool allows users to record audio with hotkeys and automatically transcribes the recording into text, pasting it directly where the cursor is located.

## Features

- Global hotkey recording controls (Alt+V to start, Alt+S to stop on Windows and Linux, Ctrl+V/Ctrl+S on macOS)
- Real-time audio recording
- Automatic transcription using Groq's Whisper API
- Cross-platform support (Windows, macOS and Linux)
- Visual feedback through status window
- Clipboard-based text insertion
- Docker support for containerized deployment

## Prerequisites

- Python 3.x
- portaudio19-dev (Linux only)
- xdotool (Linux only)
- portaudio and tcl-tk (macOS only)

## Installation

1. Clone the repository:
```bash
git clone github.com/0x4ym4n/ai-echoprompt.git
cd ai-echoprompt
```

2.Create a .env file in the root directory:

```bash
GROQ_API_KEY=your_groq_api_key_here
```

3.Install the required Python packages:

```bash
pip install -r requirements.txt
```

4.Run the application:

```bash
python audio.py
```

## Using Docker

```bash
docker build -t ai-echoprompt .
docker run -it --device /dev/snd ai-echoprompt
```

## Usage

1. Press Alt+V to start recording (Ctrl+V on macOS)
2. Speak clearly into your microphone
3. Press Alt+S to stop recording and begin transcription (Ctrl+S on macOS)
4. The transcribed text will be automatically pasted at your cursor location


## Project Structure

```
├── audio.py           # Main application script
├── Dockerfile         # Docker configuration
├── requirements.txt   # Python dependencies
|(not in repo)
├── .env               # Environment variables
└── .gitignore         # Git ignore rules
```

# Platform-Specific Notes

## Linux
* Requires portaudio19-dev and xdotool:
```bash
sudo apt-get install portaudio19-dev xdotool
```
## macOS
* Requires portaudio and tcl-tk:
```bash
brew install portaudio tcl-tk
```
Additionally, you'll need to turn on the **accessibility** feature for the **Terminal** app to be able to simulate the CMD+V paste operation through: **System Settings > Privacy & Security > Accessibility**.
## Windows
* No additional dependencies

# Contributing
Contributions are welcome!
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a new pull request

# Acknowledgements
* Groq for providing the Whisper API
* PyAudio developers for the audio interface

