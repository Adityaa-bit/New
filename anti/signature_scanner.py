import hashlib
from database_manager import DatabaseManager

class SignatureScanner:
    @staticmethod
    
    #it scan for the file that is ussed tki
    def scan(file_path):
        try:
            file_hash = SignatureScanner.calculate_file_hash(file_path)
            malware_signatures = DatabaseManager.get_all_signatures()
            return file_hash in malware_signatures
        except Exception as e:
            print(f"Error scanning file: {e}")
            return False
    # it calculate hash value of file
    @staticmethod
    def calculate_file_hash(file_path):
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()