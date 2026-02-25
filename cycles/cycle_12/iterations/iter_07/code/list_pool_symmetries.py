
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
    
    print(f"Pool size: {len(pool)}")
    print("Full list of Det=1 knots and their symmetries:")
    print(pool[['name', 'symmetry_type']].to_string())

if __name__ == "__main__":
    main()
