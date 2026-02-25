
import sys
import pandas as pd
import numpy as np
from pathlib import Path

# --- Dynamic SSoT Setup ---
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
sys.path.insert(0, str(project_root / "ssot"))
from ksau_ssot import SSOT

def main():
    ssot = SSOT()
    knots_df, _ = ssot.knot_data()
    
    # 1. Identify the Pool
    # Criteria: Det=1, Volume > 0
    knots_df['determinant'] = pd.to_numeric(knots_df['determinant'], errors='coerce')
    knots_df['volume'] = pd.to_numeric(knots_df['volume'], errors='coerce')
    
    pool = knots_df[
        (knots_df['determinant'] == 1) & 
        (knots_df['volume'] > 0)
    ].copy()
    
    print(f"Total Det=1 knots found: {len(pool)}")
    
    # Check crossing numbers
    print("Crossing numbers distribution in pool:")
    print(pool['crossing_number'].value_counts().sort_index())
    
    # The Top 10 candidates are all 12 crossings. 
    # Let's see how many of the 60 are 12 crossings.
    # Actually, v6.1 FINAL_SUMMARY says "60 Det=1 knots".
    # I will stick to the pool of these exactly 60 (or whatever number matches).
    
    # 2. Count 'fully amphicheiral' in the pool
    # 'symmetry_type' column
    pool['symmetry_type'] = pool['symmetry_type'].fillna('Unknown').astype(str).str.lower()
    fully_amphi_count = len(pool[pool['symmetry_type'].str.contains('fully amphicheiral')])
    any_amphi_count = len(pool[pool['symmetry_type'].str.contains('amphicheiral')])
    
    print(f"Fully Amphicheiral knots in pool: {fully_amphi_count}")
    print(f"Any Amphicheiral knots in pool: {any_amphi_count}")
    print(f"Pool size: {len(pool)}")

if __name__ == "__main__":
    main()
