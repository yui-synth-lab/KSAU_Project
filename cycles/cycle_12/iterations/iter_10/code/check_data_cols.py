import sys
import pandas as pd
from pathlib import Path

# --- Mandatory SSoT Setup ---
sys.path.insert(0, r"E:\Obsidian\KSAU_Project\ssot")
from ksau_ssot import SSOT

def main():
    ssot = SSOT()
    knots_df, links_df = ssot.knot_data()
    
    # Check for torsion related columns
    torsion_cols = [c for c in knots_df.columns if 'torsion' in c.lower()]
    print("Torsion columns in knots:", torsion_cols)
    
    # Check for specific particles' data
    topo = ssot.topology_assignments()
    for p in ['Electron', 'Muon', 'Tau', 'Top']:
        t_name = topo[p]['topology']
        is_link = "L" in t_name
        df = links_df if is_link else knots_df
        match = df[df['name'] == t_name]
        if not match.empty:
            print(f"\n{p} ({t_name}):")
            for col in torsion_cols:
                if col in match.columns:
                    print(f"  {col}: {match.iloc[0][col]}")

if __name__ == "__main__":
    main()
