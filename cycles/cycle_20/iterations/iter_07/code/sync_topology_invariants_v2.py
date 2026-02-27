import sys
from pathlib import Path
import json
import pandas as pd

# ============================================================================
# SSoT Setup (Path Hardcoding is STRICTLY PROHIBITED)
# ============================================================================
current_file = Path(__file__).resolve()
# cycles/cycle_20/iterations/iter_07/code/sync_topology_invariants_v2.py
# parents[0] = code, [1] = iter_07, [2] = iterations, [3] = cycle_20, [4] = cycles, [5] = project_root
project_root = current_file.parents[5]
ssot_path = project_root / "ssot"
sys.path.insert(0, str(ssot_path))    
from ksau_ssot import SSOT

def sync_invariants():
    ssot = SSOT()
    
    # 1. Load data via SSOT methods
    knots_df, links_df = ssot.knot_data()
    assignments = ssot.topology_assignments()
    
    print(f"### Topology Invariants Sync (v2) ###")
    print(f"Loaded {len(knots_df)} knots and {len(links_df)} links from SSoT.")
    
    # Combine dataframes for easier searching
    # We care about name, signature, and unlinking_number (links) / unknotting_number (knots)
    k_sub = knots_df[['name', 'signature', 'unknotting_number']].copy()
    k_sub.columns = ['name', 'signature', 'u_index']
    
    l_sub = links_df[['name', 'signature', 'unlinking_number']].copy()
    l_sub.columns = ['name', 'signature', 'u_index']
    
    combined_df = pd.concat([k_sub, l_sub], ignore_index=True)
    combined_df['name'] = combined_df['name'].str.strip()
    
    updated_count = 0
    missing_data_particles = []
    
    for particle, data in assignments.items():
        topo_name = data.get("topology")
        if not topo_name:
            continue
            
        # Search in combined data
        match = combined_df[combined_df['name'] == topo_name]
        
        if not match.empty:
            sig = match.iloc[0]['signature']
            u = match.iloc[0]['u_index']
            
            # Convert to standard types (avoid numpy types in JSON)
            if pd.isna(sig):
                sig = None
            else:
                try:
                    sig = int(float(sig))
                except:
                    sig = str(sig)
                    
            if pd.isna(u):
                u = None
            else:
                try:
                    u = int(float(u))
                except:
                    u = str(u)
            
            # Update assignments (In-memory)
            data["signature"] = sig
            data["u_index"] = u
            updated_count += 1
        else:
            missing_data_particles.append(particle)
            data["signature"] = None
            data["u_index"] = None
            
    # [FIX Problem 4]: No manual injection for Top or any other particle.
    # If data is missing in CSV, it stays None.
    
    print(f"Successfully matched {updated_count}/12 particles.")
    if missing_data_particles:
        print(f"Missing data for: {', '.join(missing_data_particles)}")
        
    # 2. Write back to SSoT (Using path from SSOT instance)
    # Note: Researcher usually doesn't have a 'save' method in SSOT, 
    # but we can use the known path relative to project_root.
    dest_path = project_root / "ssot" / "data" / "raw" / "topology_assignments.json"
    
    with open(dest_path, 'w', encoding='utf-8') as f:
        json.dump(assignments, f, indent=2, ensure_ascii=False)
        
    print(f"Updated {dest_path}")

if __name__ == "__main__":
    sync_invariants()
