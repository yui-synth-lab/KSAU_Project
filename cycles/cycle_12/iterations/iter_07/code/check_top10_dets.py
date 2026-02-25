
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
    consts = ssot.constants()
    top10 = consts.get("dark_matter_candidates", {}).get("dm_candidates_top10", [])
    
    subset = knots_df[knots_df['name'].isin(top10)]
    print("Determinants of Top 10 Candidates:")
    for _, row in subset.iterrows():
        print(f"{row['name']}: Det={row['determinant']}, Sym={row['symmetry_type']}")

if __name__ == "__main__":
    main()
