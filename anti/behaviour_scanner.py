import os

class BehaviourScanner:
    @staticmethod
    def scan(file_path):
        try:
            file_size = os.path.getsize(file_path)
            return file_size > 100 * 1024 * 1024  # 100MB
        except OSError:
            return False