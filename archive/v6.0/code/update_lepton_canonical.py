import pandas as pd
import numpy as np
import json
import ksau_config
from pathlib import Path

EPS = 1e-6

def update_lepton_by_boundary_principle():
    print("="*80)
    print("KSAU v6.0 Refinement: Lepton Assignments via Boundary Principle")
    print("Logic: choose minimal determinant knot at target crossing N (no hardcoded knot names)")
    print("="*80)
    
    # 1. Load existing assignments
    topo_path = Path('v6.0/data/topology_assignments.json')
    with open(topo_path, 'r') as f:
        assignments = json.load(f)

    phys = ksau_config.load_physical_constants()
    
    # 2. Load KnotInfo to get correct invariants
    knot_path = ksau_config.load_knotinfo_path()
    df_k = pd.read_csv(knot_path, sep='|', skiprows=[1], low_memory=False)
    df_k['crossing_number'] = pd.to_numeric(df_k['crossing_number'], errors='coerce').fillna(0)
    df_k['determinant'] = pd.to_numeric(df_k['determinant'], errors='coerce').fillna(0)
    
    print("Updating Lepton Sector...")
    for l_name, l_meta in phys['leptons'].items():
        target_n = int(l_meta.get('target_crossing', 0))
        if target_n <= 0:
            raise KeyError(f"Missing/invalid target_crossing for lepton: {l_name}")

        subset = df_k[df_k['crossing_number'] == target_n].copy()
        if subset.empty:
            raise ValueError(f"No knots found with crossing_number={target_n} for lepton {l_name}")

        # Boundary Principle: minimal determinant at fixed crossing
        row = subset.sort_values('determinant').iloc[0]
        
        assignments[l_name] = {
            "topology": str(row['name']),
            "volume": 0.0, # Boundary modes don't use volume
            "crossing_number": int(row['crossing_number']),
            "components": 1,
            "determinant": int(row['determinant']),
            "generation": int(l_meta['generation'])
        }
        print(f"  {l_name:<8}: {row['name']:<10} (N={row['crossing_number']}, Det={row['determinant']})")

    # 3. Save updated assignments
    with open(topo_path, 'w') as f:
        json.dump(assignments, f, indent=2)
    
    print(f"Success: Assignments refined by Boundary Principle at {topo_path}")

if __name__ == "__main__":
    update_lepton_by_boundary_principle()
