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
    
    # Define official names for v6.0 (Legacy from v5.0)
    OFFICIAL_QUARKS = {
        "Up": "L8a6{0}",
        "Down": "L6a4{0,0}",
        "Strange": "L10n95{0,0}",
        "Charm": "L11n64{0}",
        "Bottom": "L10a140{0,0}",
        "Top": "L11a62{0}"
    }
    
    OFFICIAL_LEPTONS = {
        "Electron": "3_1",
        "Muon": "6_1",
        "Tau": "7_1"
    }

    # Load Database Paths
    link_csv = ksau_config.load_linkinfo_path()
    knot_csv = ksau_config.load_knotinfo_path()
    
    # Load Observed Mass Data (Simplified dictionary for verification)
    # In a full run, this would come from a mass_data.csv
    OBS_MASS = {
        "Up": 2.16, "Down": 4.67, "Strange": 93.4,
        "Charm": 1270.0, "Bottom": 4180.0, "Top": 172760.0,
        "Electron": 0.511, "Muon": 105.66, "Tau": 1776.86
    }

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
            "determinant": int(row['determinant']),
            "generation": 1 if name in ["Up", "Down"] else (2 if name in ["Charm", "Strange"] else 3),
            "charge_type": "up-type" if name in ["Up", "Charm", "Top"] else "down-type",
            "observed_mass": OBS_MASS[name]
        }

    # 2. Process Leptons (Knots)
    print("Processing Leptons...")
    df_k = pd.read_csv(knot_csv, sep='|', skiprows=[1])
    for name, topo in OFFICIAL_LEPTONS.items():
        row = df_k[df_k['name'] == topo].iloc[0]
        assignments[name] = {
            "topology": topo,
            "volume": float(row['volume']),
            "crossing_number": int(row['crossing_number']),
            "components": 1,
            "determinant": int(row['determinant']),
            "generation": 1 if name == "Electron" else (2 if name == "Muon" else 3),
            "charge_type": "lepton",
            "observed_mass": OBS_MASS[name]
        }

    # 3. Save to v6.0 data directory
    output_path = Path(__file__).parent.parent / 'data' / 'topology_assignments.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(assignments, f, indent=2)
    
    print(f"\nSuccess: v6.0 Official Assignments saved to {output_path}")
    print("="*60)

if __name__ == "__main__":
    generate_v6_official_assignments()
