import numpy as np
import json
from pathlib import Path

# ============================================================================
# KSAU v7.0 Configuration
# Linking to v6.0 Single Source of Truth (SSoT)
# ============================================================================

def load_physical_constants():
    """
    Loads experimental physical constants from v6.0 SSoT.
    Path: v6.0/data/physical_constants.json
    """
    # Navigate up from v7.0/code/ to root, then to v6.0/data
    json_path = Path(__file__).parent.parent.parent / 'v6.0' / 'data' / 'physical_constants.json'
    if not json_path.exists():
        raise FileNotFoundError(f"Physical constants SSoT not found at {json_path}")
    
    with open(json_path, 'r') as f:
        return json.load(f)

def get_unified_particle_data():
    """
    Merges topology invariants (assignments) with physical constants.
    Sourced from v6.0/data/topology_assignments.json
    """
    phys = load_physical_constants()
    
    v6_data_path = Path(__file__).parent.parent.parent / 'v6.0' / 'data' / 'topology_assignments.json'
    if not v6_data_path.exists():
        raise FileNotFoundError("Topology assignments SSoT not found.")
    
    with open(v6_data_path, 'r') as f:
        assignments = json.load(f)

    # Merge physical metadata into assignments (Masses, Errors, etc.)
    for sector in ['quarks', 'leptons', 'bosons']:
        if sector not in phys: continue
        for p_name, p_meta in phys[sector].items():
            if not isinstance(p_meta, dict): continue 
            if p_name in assignments:
                # Update assignment with mass and other metadata
                assignments[p_name].update(p_meta)
    
    return assignments

# Helper alias for clarity in v7 scripts
load_data = get_unified_particle_data

def load_knotinfo_path():
    """Returns the absolute path to the knotinfo CSV file (supports .gz)."""
    # root is 3 levels up from v7.0/code/
    csv_path = Path(__file__).parent.parent.parent / 'data' / 'knotinfo_data_complete.csv'
    gz_path = csv_path.with_suffix('.csv.gz')
    return gz_path if gz_path.exists() and not csv_path.exists() else csv_path
