import pandas as pd
import json
from pathlib import Path

# Paths
project_root = Path(r"E:\Obsidian\KSAU_Project")
knot_csv = project_root / "data" / "knotinfo_data_complete.csv"
link_csv = project_root / "data" / "linkinfo_data_complete.csv"
topo_json = project_root / "ssot" / "data" / "raw" / "topology_assignments.json"

# Load JSON
with open(topo_json, 'r') as f:
    assignments = json.load(f)

# Load CSVs
k_df = pd.read_csv(knot_csv, sep="|")
l_df = pd.read_csv(link_csv, sep="|")

def get_invariants(topo_name):
    # Try LinkInfo first
    row = l_df[l_df['name'] == topo_name]
    if not row.empty:
        s = row['signature'].values[0]
        u = row['unlinking_number'].values[0]
        return s, u
    
    # Try KnotInfo
    row = k_df[k_df['name'] == topo_name]
    if not row.empty:
        s = row['signature'].values[0]
        u = row['unknotting_number'].values[0]
        return s, u
    
    return None, None

for particle, data in assignments.items():
    topo = data['topology']
    s, u = get_invariants(topo)
    
    # Handle NaN
    if pd.isna(s): s = None
    if pd.isna(u): u = None
    
    data['signature'] = s
    data['u_index'] = u

# Hardcode fix for Top as per previous Researcher's finding if still NaN
if assignments['Top']['u_index'] is None:
    assignments['Top']['u_index'] = 2 # Inferred from manual link analysis

# Write back
with open(topo_json, 'w') as f:
    json.dump(assignments, f, indent=2)

print("Updated topology_assignments.json with signature and u_index.")
