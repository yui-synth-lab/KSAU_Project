import sys
import pandas as pd
from pathlib import Path

# AIRDP SSoT Loader setup
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
ssot_path = project_root / "ssot"
sys.path.insert(0, str(ssot_path))    
from ksau_ssot import SSOT

def inspect_pool():
    ssot = SSOT()
    knots_df, links_df = ssot.knot_data()
    
    # Pool = knots + links with 3 <= n <= 12
    knots_df['crossing_number'] = pd.to_numeric(knots_df['crossing_number'], errors='coerce')
    knots_pool = knots_df[(knots_df['crossing_number'] >= 3) & (knots_df['crossing_number'] <= 12)]
    
    links_df['crossing_number'] = pd.to_numeric(links_df['crossing_number'], errors='coerce')
    links_pool = links_df[(links_df['crossing_number'] >= 3) & (links_df['crossing_number'] <= 12)]
    
    print(f"Knots in pool (3<=n<=12): {len(knots_pool)}")
    print(f"Links in pool (3<=n<=12): {len(links_pool)}")
    
    # Check leptons for 3_1, 4_1, 6_1
    lepton_knots = ["3_1", "4_1", "6_1"]
    for k in lepton_knots:
        # Check if they have the target determinant
        row = knots_pool[knots_pool['name'] == k.replace("_", "")]
        if not row.empty:
            det = row['determinant'].values[0]
            n = row['crossing_number'].values[0]
            print(f"Lepton {k}: n={n}, det={det}")

    # Check for other knots that might satisfy lepton rules
    # g=1 (n<8, det=3)
    knots_df['determinant'] = pd.to_numeric(knots_df['determinant'], errors='coerce')
    l1_candidates = knots_pool[(knots_pool['crossing_number'] < 8) & (knots_pool['determinant'] == 3)]
    print(f"Knot candidates for g=1 (n<8, det=3): {len(l1_candidates)}")
    
    l2_candidates = knots_pool[(knots_pool['crossing_number'] < 8) & (knots_pool['determinant'] == 5)]
    print(f"Knot candidates for g=2 (n<8, det=5): {len(l2_candidates)}")
    
    l3_candidates = knots_pool[(knots_pool['crossing_number'] < 8) & (knots_pool['determinant'] == 9)]
    print(f"Knot candidates for g=3 (n<8, det=9): {len(l3_candidates)}")

if __name__ == "__main__":
    inspect_pool()
