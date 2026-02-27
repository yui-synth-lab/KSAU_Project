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

def analyze_census():
    ssot = SSOT()
    k_df, l_df = ssot.knot_data()
    
    print(f"Total Knots: {len(k_df)}")
    print(f"Total Links: {len(l_df)}")
    
    # We need n, c, D
    # For knots (c=1), 'determinant' is the key.
    # For links (c>=2), 'determinant' is also the key.
    
    # Check column names
    print("Knot columns:", k_df.columns.tolist())
    print("Link columns:", l_df.columns.tolist())

if __name__ == "__main__":
    analyze_census()
