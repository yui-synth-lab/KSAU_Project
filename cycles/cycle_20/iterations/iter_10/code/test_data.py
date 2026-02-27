import sys
from pathlib import Path
import json
import pandas as pd
import numpy as np

# SSOT Setup
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
ssot_path = project_root / "ssot"
sys.path.insert(0, str(ssot_path))    
from ksau_ssot import SSOT

def test_data():
    ssot = SSOT()
    k_df, l_df = ssot.knot_data()
    
    print("Knot Determinant Samples:", k_df['determinant'].head(10).tolist())
    print("Link Determinant Samples:", l_df['determinant'].head(10).tolist())
    
    # Try to convert to numeric
    k_det = pd.to_numeric(k_df['determinant'], errors='coerce')
    l_det = pd.to_numeric(l_df['determinant'], errors='coerce')
    
    print(f"Knots with valid numeric determinant: {k_det.notna().sum()} / {len(k_df)}")
    print(f"Links with valid numeric determinant: {l_det.notna().sum()} / {len(l_df)}")

if __name__ == "__main__":
    test_data()
