import os
import numpy as np
import joblib
import hashlib

MODEL_PATH = "models/ml_detector.pkl"
SCALER_PATH = "models/scaler.pkl"

# Load trained model and scaler
model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

def extract_static_features(file_path):
    """
    Extracts basic static features from a file.
    (For demonstration; can be replaced with real PE analysis for malware files)
    """
    try:
        size = os.path.getsize(file_path)
        with open(file_path, "rb") as f:
            data = f.read()
        entropy = -np.sum([p * np.log2(p) for p in np.bincount(np.frombuffer(data, dtype=np.uint8)) / len(data) if p > 0])
        md5 = int(hashlib.md5(data).hexdigest(), 16) % (10 ** 8)
        return np.array([size, entropy, md5])
    except Exception as e:
        print(f"Error extracting features from {file_path}: {e}")
        return np.zeros(3)

def predict_file(file_path):
    features = extract_static_features(file_path).reshape(1, -1)
    features_scaled = scaler.transform(features)
    prediction = model.predict(features_scaled)[0]
    label = "Malicious" if prediction == 1 else "Benign"
    print(f"[+] File: {file_path} → {label}")
    return label

# Example use:
if __name__ == "__main__":
    test_file = "dataset/sample_test.exe"  # replace with actual file path
    predict_file(test_file)
