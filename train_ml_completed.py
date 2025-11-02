"""
train_ml_completed.py
A self-contained training script that:
- Loads dataset/dummy_dataset.csv (or dataset/*.csv)
- Trains a RandomForest classifier on byte-histograms + entropy + size
- Saves trained model to models/model.pkl and a JSON with feature names
- Prints evaluation metrics
Usage: python train_ml_completed.py
"""
import pandas as pd, joblib, json, glob, os
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report, accuracy_score

BASE = Path(__file__).resolve().parent
DATA_GLOB = BASE/"dataset" / "*.csv"
OUT_MODEL = BASE/"models"/"model.pkl"
OUT_META = BASE/"models"/"model_meta.json"

def load_dataset():
    files = list(DATA_GLOB.glob("*.csv")) if DATA_GLOB.exists() else list(BASE.glob("dataset/*.csv"))
    if not files:
        raise FileNotFoundError("No CSV dataset found in dataset/*.csv. Run generate_dummy_data.py to create synthetic data.")
    df = None
    for f in files:
        if df is None:
            df = pd.read_csv(f)
        else:
            df = pd.concat([df, pd.read_csv(f)], ignore_index=True)
    return df

def prepare_features(df):
    # Expect columns: label, entropy, size, b0..b255
    feature_cols = [c for c in df.columns if c!="label"]
    X = df[feature_cols]
    y = df["label"].astype(int)
    return X, y, feature_cols

def train_and_save(df):
    X, y, feature_cols = prepare_features(df)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="mean")),
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1))
    ])
    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_test)
    print("Accuracy:", accuracy_score(y_test, preds))
    print(classification_report(y_test, preds))
    # Save model and metadata
    joblib.dump(pipeline, OUT_MODEL)
    with open(OUT_META, "w") as fh:
        json.dump({"features": feature_cols, "model_file": str(OUT_MODEL)}, fh)
    print("Saved model to", OUT_MODEL)

if __name__=="__main__":
    df = load_dataset()
    train_and_save(df)
