import os
import random
import math
import csv
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, confusion_matrix
import joblib
import warnings
warnings.filterwarnings("ignore")

# ========== STEP 1: Dummy Data Generation ==========
def generate_dummy_files():
    os.makedirs("dataset/benign", exist_ok=True)
    os.makedirs("dataset/malicious", exist_ok=True)

    # Create benign files
    for i in range(30):
        path = f"dataset/benign/file{i}.txt"
        with open(path, "w") as f:
            f.write("SAFE_FILE_CONTENT_" + "A" * random.randint(100, 1000))

    # Create malicious files
    for i in range(30):
        path = f"dataset/malicious/malware{i}.exe"
        with open(path, "w") as f:
            f.write("MALWARE_PAYLOAD_" + "X" * random.randint(500, 2000))

    print("[+] Dummy benign and malicious files generated.")


# ========== STEP 2: Feature Extraction ==========
def calculate_entropy(data):
    """Simple Shannon entropy calculation."""
    if not data:
        return 0
    entropy = 0
    for x in set(data):
        p_x = float(data.count(x)) / len(data)
        entropy += -p_x * math.log2(p_x)
    return entropy


def extract_features(file_path):
    try:
        size = os.path.getsize(file_path)
        ext = os.path.splitext(file_path)[1]
        with open(file_path, "rb") as f:
            content = f.read(1024)  # limit for speed
            entropy = calculate_entropy(list(content))
        return [file_path, size, entropy, ext]
    except Exception as e:
        return [file_path, 0, 0, ""]


# ========== STEP 3: Dataset Creation ==========
def create_dataset_csv():
    rows = []

    # Process benign files
    for file in os.listdir("dataset/benign"):
        file_path = os.path.join("dataset/benign", file)
        rows.append(extract_features(file_path) + [0])  # label 0 = benign

    # Process malicious files
    for file in os.listdir("dataset/malicious"):
        file_path = os.path.join("dataset/malicious", file)
        rows.append(extract_features(file_path) + [1])  # label 1 = malicious

    csv_path = "dataset/dummy_dataset.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["file_path", "size", "entropy", "extension", "label"])
        writer.writerows(rows)

    print(f"[+] Dataset CSV created at {csv_path}")
    return csv_path


# ========== STEP 4: Train and Compare ML Models ==========
def train_and_compare_models(dataset_path):
    print("[+] Loading dataset...")
    df = pd.read_csv(dataset_path)

    df["extension"] = df["extension"].astype("category").cat.codes
    X = df[["size", "entropy", "extension"]]
    y = df["label"]

    # Add small noise so model doesn’t overfit perfectly
    X["entropy"] += np.random.normal(0, 0.05, X.shape[0])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    models = {
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "SVM": SVC(kernel="rbf", probability=True, random_state=42)
    }

    results = []
    best_model = None
    best_f1 = 0

    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else y_pred

        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_proba)
        tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
        tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0

        results.append((name, acc, f1, auc, tpr, fpr))

        print(f"\n=== {name} ===")
        print(f"Accuracy: {acc:.4f}")
        print(f"F1-Score: {f1:.4f}")
        print(f"AUC-ROC: {auc:.4f}")
        print(f"TPR: {tpr:.4f}")
        print(f"FPR: {fpr:.4f}")

        # Track best model
        if f1 > best_f1:
            best_f1 = f1
            best_model = model

    # Save the best model
    os.makedirs("models", exist_ok=True)
    joblib.dump(best_model, "models/ml_detector.pkl")
    print("\n[+] Best model saved as models/ml_detector.pkl")

    # Display summary table
    print("\n=== Summary of All Models ===")
    print("{:<15} {:<10} {:<10} {:<10} {:<10} {:<10}".format("Model", "Acc", "F1", "AUC", "TPR", "FPR"))
    for name, acc, f1, auc, tpr, fpr in results:
        print(f"{name:<15} {acc:<10.4f} {f1:<10.4f} {auc:<10.4f} {tpr:<10.4f} {fpr:<10.4f}")


# ========== MAIN EXECUTION ==========
if __name__ == "__main__":
    print("[*] Starting ML training pipeline...")
    generate_dummy_files()
    dataset_path = create_dataset_csv()
    train_and_compare_models(dataset_path)
