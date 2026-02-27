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
    knots_df, links_df = ssot.knot_data()
    
    print("Knots with Det % 24 == 0 (n <= 10):")
    if not knots_df.empty:
        knots_df['determinant'] = pd.to_numeric(knots_df['determinant'], errors='coerce')
        knots_df['crossing_number'] = pd.to_numeric(knots_df['crossing_number'], errors='coerce')
        target_knots = knots_df[(knots_df['determinant'] % 24 == 0) & (knots_df['crossing_number'] <= 10)]
        print(target_knots[['name', 'crossing_number', 'determinant']])
    
    print("\nLinks with Det % 24 == 0 (n <= 10):")
    if not links_df.empty:
        # Linkinfo might have different columns. Let's check first.
        # print(links_df.columns.tolist())
        if 'determinant' in links_df.columns:
            links_df['determinant'] = pd.to_numeric(links_df['determinant'], errors='coerce')
            links_df['crossing_number'] = pd.to_numeric(links_df['crossing_number'], errors='coerce')
            target_links = links_df[(links_df['determinant'] % 24 == 0) & (links_df['crossing_number'] <= 10)]
            print(target_links[['name', 'crossing_number', 'determinant']])

if __name__ == "__main__":
    main()
