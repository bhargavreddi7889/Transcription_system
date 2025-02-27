import os
import time
import whisper
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json

# Configuration
WATCH_DIR = r"C:\Users\Bharghav\OneDrive\Desktop\transcription system\media_folder"
PROCESSED_FILES_TRACKER = os.path.join(WATCH_DIR, "processed_files.json")
SUPPORTED_FORMATS = (".mp3", ".wav", ".mp4", ".mkv", ".mov", ".flv", ".aac", ".m4a")

# Load processed files
if os.path.exists(PROCESSED_FILES_TRACKER):
    with open(PROCESSED_FILES_TRACKER, "r") as f:
        processed_files = json.load(f)
else:
    processed_files = {}

def save_processed_files():
    with open(PROCESSED_FILES_TRACKER, "w") as f:
        json.dump(processed_files, f)


def transcribe_file(file_path, language="en"):
    if file_path in processed_files:
        print(f"Skipping already processed file: {file_path}")
        return

    try:
        model = whisper.load_model("medium")
        result = model.transcribe(file_path, language=language)
        print(result)
        transcript_path = f"{file_path}.txt"
        
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(result['text'])
        
        processed_files[file_path] = True
        save_processed_files()

        print(f"Transcription saved to: {transcript_path}")
    except Exception as e:
        print(f"Error transcribing {file_path}: {e}")



def scan_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(SUPPORTED_FORMATS):
                file_path = os.path.join(root, file)
                transcribe_file(file_path)


class FileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(SUPPORTED_FORMATS):
            print(f"New file detected: {event.src_path}")
            transcribe_file(event.src_path)


def main():
    print(f"Starting transcription system. Monitoring folder: {WATCH_DIR}")

    # Initial scan to catch any files already in the folder
    scan_directory(WATCH_DIR)

    # Start watching for new files
    event_handler = FileHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIR, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping transcription system...")
        observer.stop()

    observer.join()


if __name__ == "__main__":
    main()


