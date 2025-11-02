"""
generate_dummy_data.py
Creates a synthetic dataset of "file-like" byte histograms and entropy for malware vs benign samples.
Outputs CSV to dataset/dummy_dataset.csv
"""
import numpy as np, pandas as pd, os, math, secrets
from pathlib import Path
def byte_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    freq = [0]*256
    for b in data:
        freq[b]+=1
    probs = [f/len(data) for f in freq if f>0]
    import math
    return -sum(p*math.log2(p) for p in probs)

def make_sample(malware: bool):
    # malware tends to have higher entropy and some skew in byte distributions (this is synthetic)
    length = secrets.choice(range(1024, 20000)) if malware else secrets.choice(range(512, 15000))
    data = secrets.token_bytes(length)
    # Inject a pattern for malware: flip some bytes to higher values
    if malware:
        data = bytearray(data)
        for _ in range(max(1, length//2000)):
            i = secrets.randbelow(length)
            data[i] = (data[i] + secrets.choice([7,13,29,47])) % 256
        data = bytes(data)
    hist = [0]*256
    for b in data:
        hist[b]+=1
    hist_norm = [h/len(data) for h in hist]
    ent = byte_entropy(data)
    return hist_norm, ent, len(data)

def generate(n_malware=1000, n_benign=1000, out="dataset/dummy_dataset.csv"):
    rows = []
    for _ in range(n_malware):
        hist, ent, length = make_sample(True)
        rows.append({"label":1, "entropy":ent, "size":length, **{f"b{i}":hist[i] for i in range(256)}})
    for _ in range(n_benign):
        hist, ent, length = make_sample(False)
        rows.append({"label":0, "entropy":ent, "size":length, **{f"b{i}":hist[i] for i in range(256)}})
    import pandas as pd
    df = pd.DataFrame(rows)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Saved {len(df)} rows to {out}")

if __name__=="__main__":
    generate(500, 500, out="dataset/dummy_dataset.csv")
