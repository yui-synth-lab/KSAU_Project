import pandas as pd
import json
import ksau_config
from pathlib import Path

def generate_v6_official_assignments():
    """
    Re-generates the official v6.0 assignments from CSV data 
    to ensure data integrity and track provenance.
    """
    print("="*60)
    print("KSAU v6.0: Official Topology Assignment Generator")
    print("="*60)
    
    # Official Topology Assignments (Truth)
    OFFICIAL_QUARKS = {
        'Up': 'L8a6{0}', 'Charm': 'L11n64{0}', 'Top': 'L11a62{0}',
        'Down': 'L6a4{0,0}', 'Strange': 'L10n95{0,0}', 'Bottom': 'L10a140{0,0}'
    }
    OFFICIAL_LEPTONS = {
        'Electron': '3_1', 'Muon': '6_1', 'Tau': '7_1'
    }
    OFFICIAL_BOSONS = {
        'W': 'L11n387{0,0,0}', 'Z': 'L11a431{0,0,0}', 'Higgs': 'L11a55{0,0}'
    }

    # Load Database Paths
    link_csv = ksau_config.load_linkinfo_path()
    knot_csv = ksau_config.load_knotinfo_path()
    
    # Use mass data from physical_constants.json as well
    assignments = {}

    # 1. Process Quarks (Links)
    print("Processing Quarks...")
    df_l = pd.read_csv(link_csv, sep='|', skiprows=[1])
    for name, topo in OFFICIAL_QUARKS.items():
        row = df_l[df_l['name'] == topo].iloc[0]
        assignments[name] = {
            "topology": topo,
            "volume": float(row['volume']),
            "crossing_number": int(row['crossing_number']),
            "components": int(row['components']),
            "determinant": int(row['determinant'])
        }

    # 2. Process Leptons (Knots)
    print("Processing Leptons...")
    df_k = pd.read_csv(knot_csv, sep='|', skiprows=[1], low_memory=False)
    for name, topo in OFFICIAL_LEPTONS.items():
        row = df_k[df_k['name'] == topo].iloc[0]
        assignments[name] = {
            "topology": topo,
            "volume": float(row['volume']) if str(row['volume']) != 'Not Hyperbolic' else 0.0,
            "crossing_number": int(row['crossing_number']) if 'crossing_number' in row else int(topo.split('_')[0]),
            "components": 1,
            "determinant": int(row['determinant'])
        }

    # 3. Process Bosons (Links)
    print("Processing Bosons...")
    for name, topo in OFFICIAL_BOSONS.items():
        # Try to find exactly, or by prefix if {0,0,0} suffix varies
        matches = df_l[df_l['name'].str.startswith(topo.split('{')[0])]
        if matches.empty:
            print(f"Warning: Could not find boson {name} ({topo})")
            continue
        row = matches.iloc[0]
        assignments[name] = {
            "topology": topo,
            "volume": float(row['volume']),
            "crossing_number": int(row['crossing_number']),
            "components": int(row['components']),
            "determinant": int(row['determinant']),
            "is_brunnian": True
        }

    # 4. Save to v6.0 data directory
    output_path = Path(__file__).parent.parent / 'data' / 'topology_assignments.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(assignments, f, indent=2)
    
    print(f"\nSuccess: v6.0 Official Assignments saved to {output_path}")
    print("="*60)

if __name__ == "__main__":
    generate_v6_official_assignments()
