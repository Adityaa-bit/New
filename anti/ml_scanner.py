# ml_scanner.py
import os
import math
import pickle

class MLScanner:
    MODEL_PATH = os.path.join("models", "ml_detector.pkl")
    SCALER_PATH = os.path.join("models", "scaler.pkl")

    def __init__(self):
        self.model = None
        self.scaler = None

        # Load model
        if os.path.exists(self.MODEL_PATH):
            with open(self.MODEL_PATH, "rb") as f:
                self.model = pickle.load(f)
        else:
            print("[!] ML model not found, skipping ML scan.")

        # Load scaler
        if os.path.exists(self.SCALER_PATH):
            with open(self.SCALER_PATH, "rb") as f:
                self.scaler = pickle.load(f)

    def _file_entropy(self, path):
        """Calculate Shannon entropy of the file contents."""
        try:
            with open(path, "rb") as f:
                data = f.read()
            if not data:
                return 0.0
            freq = [0] * 256
            for b in data:
                freq[b] += 1
            entropy = 0.0
            for c in freq:
                if c == 0: 
                    continue
                p = c / len(data)
                entropy -= p * math.log2(p)
            return entropy
        except Exception:
            return 0.0

    def _extract_features(self, path):
        """Extract simple static features from file."""
        try:
            size = os.path.getsize(path)
            entropy = self._file_entropy(path)
            ext = os.path.splitext(path)[1].lower()
            risky_ext = int(ext in {".exe", ".dll", ".vbs", ".js", ".jar", ".scr", ".bat"})
            return [[size, entropy, risky_ext]]
        except Exception:
            return [[0, 0.0, 0]]

    def scan(self, file_path):
        """Return True if file is malicious according to ML model."""
        if not self.model:
            return False  # fallback if no model
        try:
            X = self._extract_features(file_path)
            if self.scaler:
                X = self.scaler.transform(X)
            proba = self.model.predict_proba(X)[0][1]  # malware probability
            return proba >= 0.5  # threshold
        except Exception as e:
            print("[MLScanner] Error:", e)
            return False
