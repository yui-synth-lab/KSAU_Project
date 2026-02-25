import sys
import pandas as pd
from pathlib import Path

# --- Dynamic SSoT Setup ---
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
sys.path.insert(0, str(project_root / "ssot"))
from ksau_ssot import SSOT

def main():
    ssot = SSOT()
    knots_df, _ = ssot.knot_data()
    
    knots_df['determinant_num'] = pd.to_numeric(knots_df['determinant'], errors='coerce')
    knots_df['volume_num'] = pd.to_numeric(knots_df['volume'], errors='coerce')
    
    pool = knots_df[
        (knots_df['determinant_num'] == 1) & 
        (knots_df['volume_num'] > 0)
    ].copy()
    
    print(f"Pool size: {len(pool)}")
    print("Unique symmetry types in pool:")
    print(pool['symmetry_type'].unique())
    
    print("\nCounting symmetries in pool (case-insensitive):")
    pool['sym_lower'] = pool['symmetry_type'].fillna('Unknown').astype(str).str.lower()
    print(pool['sym_lower'].value_counts())

if __name__ == "__main__":
    main()
