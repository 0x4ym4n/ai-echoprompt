#!/usr/bin/env python3
import threading
import wave
import requests
import pyaudio
import tkinter as tk
from queue import Queue
from pynput import keyboard
from pynput.keyboard import Controller
import subprocess
import time
import platform
import pyperclip  # type: ignore # New import for clipboard operations
from pynput.keyboard import Controller, Key
from dotenv import load_dotenv
import os

# Define functions for window focus handling based on OS
if platform.system() == 'Linux':
    def get_active_window():
        try:
            window_id = subprocess.check_output(["xdotool", "getactivewindow"]).decode().strip()
            print("Active window id:", window_id)
            return window_id
        except Exception as e:
            print("Error getting active window:", e)
            return None

    def activate_window(window_id):
        try:
            subprocess.run(["xdotool", "windowactivate", window_id])
        except Exception as e:
            print("Error activating window:", e)
else:
    import pygetwindow as gw
    def get_active_window():
        try:
            window = gw.getActiveWindow()
            print("Captured active window:", window)
            return window
        except Exception as e:
            print("Error getting active window:", e)
            return None

    def activate_window(window):
        try:
            window.activate()
        except Exception as e:
            print("Error activating window:", e)

# Global variables
recorder = None
focused_window = None  # Will store the originally focused window (or window id on Linux)
gui_queue = Queue()  # For thread-safe GUI updates

class AudioRecorder:
    def __init__(self, filename="temp.wav", channels=1, rate=16000, chunk=1024):
        self.filename = filename
        self.channels = channels
        self.rate = rate
        self.chunk = chunk
        self.frames = []
        self.recording = False
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.thread = None

    def start(self):
        self.frames = []
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        self.recording = True
        self.thread = threading.Thread(target=self.record)
        self.thread.start()
        print("Recording started...")

    def record(self):
        while self.recording:
            try:
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                self.frames.append(data)
            except Exception as e:
                print("Error during recording:", e)
                self.recording = False
                break

    def stop(self):
        if not self.recording:
            return
        self.recording = False
        if self.thread.is_alive():
            self.thread.join()
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.save_wav()
        print(f"Recording stopped. Audio saved to {self.filename}")

    def save_wav(self):
        wf = wave.open(self.filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()

    def terminate(self):
        self.p.terminate()

def transcribe_audio(filename):
    # Whisper API parameters
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("Error: GROQ_API_KEY not found in environment variables")
        return None
    base_url = "https://api.groq.com/openai/v1"
    model = "whisper-large-v3"
    endpoint = f"{base_url}/audio/transcriptions"

    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": model,
        "language":"en"
    }
    try:
        with open(filename, "rb") as audio_file:
            files = {"file": audio_file}
            print("Sending audio for transcription...")
            response = requests.post(endpoint, headers=headers, data=data, files=files)
            response.raise_for_status()
            result = response.json()
            transcript = result.get("text", "")
            return transcript
    except Exception as e:
        print("Error transcribing audio:", e)
        return None

class StatusWindow:
    def __init__(self, root):
        self.top = tk.Toplevel(root)
        self.top.title("Status")
        self.label = tk.Label(self.top, text="", font=('Arial', 14))
        self.label.pack(padx=20, pady=10)
        self._center_window()
        self.top.attributes('-topmost', True)
    
    def _center_window(self):
        self.top.update_idletasks()
        width = self.top.winfo_width()
        height = self.top.winfo_height()
        x = (self.top.winfo_screenwidth() // 2) - (width // 2)
        y = (self.top.winfo_screenheight() // 2) - (height // 2)
        self.top.geometry(f'+{x}+{y}')
    
    def update_text(self, message):
        self.label.config(text=message)
        self._center_window()
    
    def close(self):
        self.top.destroy()

def on_start(root):
    global recorder, focused_window
    # Capture the currently active window BEFORE showing the status window
    focused_window = get_active_window()
    if focused_window:
        print("Captured focused window:", focused_window)
    else:
        print("No focused window captured.")
    if recorder is None or not recorder.recording:
        recorder = AudioRecorder(filename="temp.wav")
        recorder.start()
        gui_queue.put(('show', "Recording..."))
    else:
        print("Already recording!")

def transcribe_and_type():
    global focused_window
    if recorder:
        gui_queue.put(('update', "Transcribing..."))
        transcript = transcribe_audio(recorder.filename)
        if transcript:
            print("Transcript:", transcript)
            # Close the status window
            gui_queue.put(('close',))
            # Wait briefly to ensure the status window has closed
            time.sleep(0.2)
            # Refocus the originally active window
            if focused_window:
                activate_window(focused_window)
                print("Refocused to the original window.")
            # Copy transcript to clipboard instead of typing character-by-character
            pyperclip.copy(transcript)
            time.sleep(0.2)
            kb = Controller()
            # Simulate Ctrl+V paste operation
            kb.press(Key.ctrl)
            kb.press('v')
            kb.release('v')
            kb.release(Key.ctrl)
            print("Transcript pasted via clipboard.")
        else:
            print("Failed to transcribe.")
            gui_queue.put(('close',))
    else:
        gui_queue.put(('close',))


def on_stop():
    global recorder
    if recorder is not None and recorder.recording:
        recorder.stop()
        threading.Thread(target=transcribe_and_type).start()
    else:
        print("No recording in progress.")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide main window
    status_window = None

    # Set up hotkeys
    hotkeys = keyboard.GlobalHotKeys({
        '<alt>+v': lambda: on_start(root),
        '<alt>+s': on_stop
    })
    hotkeys.start()

    print("Ready:")
    print("  Press Alt+V to start recording.")
    print("  Press Alt+S to stop recording and transcribe.")

    try:
        while True:
            # Process GUI updates from queue
            while not gui_queue.empty():
                command, *args = gui_queue.get_nowait()
                if command == 'show':
                    if status_window:
                        status_window.close()
                    status_window = StatusWindow(root)
                    status_window.update_text(args[0])
                elif command == 'update':
                    if status_window:
                        status_window.update_text(args[0])
                elif command == 'close':
                    if status_window:
                        status_window.close()
                    status_window = None
            root.update_idletasks()
            root.update()
            hotkeys.join(timeout=0.1)
    except KeyboardInterrupt:
        print("\nExiting...")
        hotkeys.stop()
        if recorder:
            recorder.stop()
            recorder.terminate()
        if status_window:
            status_window.close()
        root.destroy()

