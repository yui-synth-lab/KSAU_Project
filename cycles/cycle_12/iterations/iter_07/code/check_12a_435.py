
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
    
    knot = knots_df[knots_df['name'] == '12a_435']
    if knot.empty:
        print("Knot 12a_435 not found!")
    else:
        print(f"Knot: {knot.iloc[0]['name']}")
        print(f"Determinant: {knot.iloc[0]['determinant']}")
        print(f"Volume: {knot.iloc[0]['volume']}")
        print(f"Symmetry: {knot.iloc[0]['symmetry_type']}")

if __name__ == "__main__":
    main()
