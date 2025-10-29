import os
#file extensions for malware/ threat
class HeuristicScanner:
    SUSPICIOUS_EXTENSIONS = [
        ".exe", ".dll", ".bat", ".vbs", ".js", ".jar", ".scr", ".com"
    ]
    
    #it scans file for the heuristic scanner
    @staticmethod
    def scan(file_path):
        file_name = os.path.basename(file_path).lower()
        return any(file_name.endswith(ext) for ext in HeuristicScanner.SUSPICIOUS_EXTENSIONS)