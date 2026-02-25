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
    
    # Pool definition: Det=1, Volume > 0
    knots_df['determinant_num'] = pd.to_numeric(knots_df['determinant'], errors='coerce')
    knots_df['volume_num'] = pd.to_numeric(knots_df['volume'], errors='coerce')
    
    pool = knots_df[
        (knots_df['determinant_num'] == 1) & 
        (knots_df['volume_num'] > 0)
    ].copy()
    
    pool_size = len(pool)
    print(f"Total Det=1 knots found: {pool_size}")
    
    # Count symmetry types
    pool['sym_lower'] = pool['symmetry_type'].fillna('Unknown').astype(str).str.lower()
    
    print("\nSymmetry counts in the pool:")
    print(pool['sym_lower'].value_counts())
    
    fully_amphi_count = len(pool[pool['sym_lower'].str.contains('fully amphicheiral')])
    print(f"\nFully Amphicheiral count in pool: {fully_amphi_count}")

if __name__ == "__main__":
    main()
