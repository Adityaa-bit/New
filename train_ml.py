# train_ml.py
import os
import math
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

# === Feature extraction (same as ml_scanner.py) ===
def file_entropy(path):
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

def extract_features(path):
    try:
        size = os.path.getsize(path)
        entropy = file_entropy(path)
        ext = os.path.splitext(path)[1].lower()
        risky_ext = int(ext in {".exe", ".dll", ".vbs", ".js", ".jar", ".scr", ".bat"})
        return [size, entropy, risky_ext]
    except Exception:
        return [0, 0.0, 0]

# === Build dataset ===
def build_dataset(benign_dir, malicious_dir):
    data = []
    labels = []

    for root, _, files in os.walk(benign_dir):
        for f in files:
            path = os.path.join(root, f)
            data.append(extract_features(path))
            labels.append(0)  # 0 = benign

    for root, _, files in os.walk(malicious_dir):
        for f in files:
            path = os.path.join(root, f)
            data.append(extract_features(path))
            labels.append(1)  # 1 = malicious

    return np.array(data), np.array(labels)

# === Training pipeline ===
def train_model(benign_dir="dataset/benign", malicious_dir="dataset/malicious"):
    X, y = build_dataset(benign_dir, malicious_dir)
    if len(X) == 0:
        print("❌ No training data found. Add files to dataset folders.")
        return

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Scale features
    scaler = StandardScaler().fit(X_train)
    X_train = scaler.transform(X_train)
    X_test = scaler.transform(X_test)

    # Train XGBoost model
    model = XGBClassifier(n_estimators=200, use_label_encoder=False, eval_metric="logloss")
    model.fit(X_train, y_train)

    # Evaluate
    print("✅ Train Accuracy:", model.score(X_train, y_train))
    print("✅ Test Accuracy:", model.score(X_test, y_test))

    # Save model + scaler
    os.makedirs("models", exist_ok=True)
    with open("models/ml_detector.pkl", "wb") as f:
        pickle.dump(model, f)
    with open("models/scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)

    print("🎉 Model and scaler saved in /models/")

if __name__ == "__main__":
    train_model()
