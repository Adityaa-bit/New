import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from file_scanner import FileScanner

class FileChangeHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            print(f"File created: {event.src_path}")
            FileScanner.scan_file(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            print(f"File modified: {event.src_path}")
            FileScanner.scan_file(event.src_path)

class FileMonitoring:
    @staticmethod
    def monitor_directory(path):
        if not os.path.exists(path):
            print(f"Directory not found: {path}")
            return

        event_handler = FileChangeHandler()
        observer = Observer()
        observer.schedule(event_handler, path, recursive=True)
        observer.start()

        try:
            print(f"Monitoring directory: {path}")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()