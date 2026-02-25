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
    
    knots_df['determinant'] = pd.to_numeric(knots_df['determinant'], errors='coerce')
    knots_df['volume'] = pd.to_numeric(knots_df['volume'], errors='coerce')
    
    pool = knots_df[
        (knots_df['determinant'] == 1) & 
        (knots_df['volume'] > 0)
    ].copy()
    
    print("Unique symmetry types in pool:")
    print(pool['symmetry_type'].unique())
    
    # Check for Top 10 candidates specifically
    consts = ssot.constants()
    top10 = consts.get("dark_matter_candidates", {}).get("dm_candidates_top10", [])
    
    print("\nSymmetry of Top 10 Candidates:")
    top10_data = knots_df[knots_df['name'].isin(top10)]
    for _, row in top10_data.iterrows():
        print(f"{row['name']}: {row['symmetry_type']}")

if __name__ == "__main__":
    main()
