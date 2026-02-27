import sys
from pathlib import Path
import pandas as pd

# AIRDP SSoT Loader setup
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
ssot_path = project_root / "ssot"
sys.path.insert(0, str(ssot_path))    
from ksau_ssot import SSOT

def main():
    ssot = SSOT()
    knots_df, _ = ssot.knot_data()
    
    dm_candidates = ["12a_435", "12a_462", "12a_125"]
    
    print("Checking DM candidates for Det % 24 == 0:")
    for name in dm_candidates:
        # KnotInfo uses names like '12a435' or '12a_435'?
        # Let's check the column names and sample data
        pass

    # Search for names in knots_df
    # Note: Column for name is usually 'name' or 'knot'
    # Let's check columns first
    print(f"Columns: {knots_df.columns.tolist()[:10]}")
    
    # Try to find the candidates
    for name in dm_candidates:
        # Try both formats
        target = name.replace("_", "")
        row = knots_df[knots_df['name'] == target]
        if row.empty:
            row = knots_df[knots_df['name'] == name]
        
        if not row.empty:
            det = row['determinant'].values[0]
            print(f"Candidate {name}: Det = {det}, Det % 24 = {int(det) % 24}")
        else:
            print(f"Candidate {name} not found in knots_df")

if __name__ == "__main__":
    main()
