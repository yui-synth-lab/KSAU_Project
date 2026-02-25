import sys
import pandas as pd
from pathlib import Path

# --- Mandatory SSoT Setup ---
sys.path.insert(0, r"E:\Obsidian\KSAU_Project\ssot")
from ksau_ssot import SSOT

def main():
    ssot = SSOT()
    _, links_df = ssot.knot_data()
    
    # Check for torsion related columns in links
    torsion_cols = [c for c in links_df.columns if 'torsion' in c.lower()]
    print("Torsion columns in links:", torsion_cols)
    
    # Check for Top (L11a225{1})
    topo = ssot.topology_assignments()
    t_name = topo['Top']['topology']
    match = links_df[links_df['name'] == t_name]
    if not match.empty:
        print(f"\nTop ({t_name}):")
        for col in torsion_cols:
            if col in match.columns:
                print(f"  {col}: {match.iloc[0][col]}")

if __name__ == "__main__":
    main()
