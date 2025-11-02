# Antivirus - Completed training pipeline (synthetic)

This package supplies a simple completed training pipeline for malware detection based on byte-level histograms.
Files created:
- generate_dummy_data.py : Creates a synthetic dataset at dataset/dummy_dataset.csv
- train_ml_completed.py : Loads dataset/*.csv, trains a RandomForest, saves model to models/model.pkl
- requirements.txt

Usage (on your machine):
1. Install dependencies:
   pip install -r requirements.txt
2. Generate data (optional, if you don't have real dataset):
   python generate_dummy_data.py
3. Train model:
   python train_ml_completed.py
4. The trained model will be saved at models/model.pkl

Notes:
- This pipeline is intentionally simple and meant as a starting point to integrate into the GitHub repo.
- For a real project, use labelled real malware samples and follow legal/ethical rules for handling malware.
