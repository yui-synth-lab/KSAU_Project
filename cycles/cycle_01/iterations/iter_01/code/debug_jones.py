import pandas as pd
import numpy as np
from pathlib import Path
import json

def parse_jones_vector(vector_str, q):
    if pd.isna(vector_str) or vector_str == 'undefined' or not isinstance(vector_str, str):
        return None
    parts = vector_str.strip('{}').split(',')
    if len(parts) < 3:
        return None
    try:
        min_pow = int(parts[0])
        coeffs = [float(c) for c in parts[2:]]
        val = 0j
        for i, c in enumerate(coeffs):
            p = min_pow + i
            val += c * (q**p)
        return abs(val)
    except Exception as e:
        return None

def debug():
    base_path = Path(r"E:\Obsidian\KSAU_Project\data")
    knot_path = base_path / 'knotinfo_data_complete.csv'
    df = pd.read_csv(knot_path, sep='|', skiprows=[1], low_memory=False, nrows=100)
    
    q = np.exp(1j * 2 * np.pi / 5)
    print("Sample Jones Evaluation:")
    for i, row in df.iterrows():
        name = row['name']
        js = row['jones_polynomial_vector']
        val = parse_jones_vector(js, q)
        if val is not None:
            print(f"{name}: Jones={js[:30]}... Eval={val:.4f}")
        else:
            print(f"{name}: Jones={js} Eval=None")

if __name__ == "__main__":
    debug()
