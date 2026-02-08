import numpy as np
import json
from pathlib import Path

# ============================================================================
# THEORETICAL CONSTANTS (The Laws of KSAU)
# ============================================================================
KAPPA = np.pi / 24
ALPHA_GEOM = np.pi / 432
BQ_DEFAULT = -(7 + 7 * KAPPA)

def get_kappa_coeffs():
    """Returns the standard coefficients for mass formulas."""
    return {
        'quark_vol': 10 * KAPPA,
        'quark_twist': KAPPA,
        'quark_intercept': BQ_DEFAULT,
        'lepton_n2': (14/9) * KAPPA,
        'lepton_twist_correction': -1/6
    }

# ============================================================================
# DATA LOADING
# ============================================================================

def load_physical_constants():
    """Loads experimental physical constants from JSON."""
    json_path = Path(__file__).parent.parent / 'data' / 'physical_constants.json'
    if not json_path.exists():
        raise FileNotFoundError(f"Physical constants not found at {json_path}")
    
    with open(json_path, 'r') as f:
        return json.load(f)

def load_topology_assignments():
    """
    Loads topology assignments. 
    Prioritizes v6.0 data, falls back to v5.0.
    """
    # 1. Try local v6.0 data first
    v6_data_path = Path(__file__).parent.parent / 'data' / 'topology_assignments.json'
    if v6_data_path.exists():
        with open(v6_data_path, 'r') as f:
            return json.load(f)
            
    # 2. Fallback to v5.0 data
    root_dir = Path(__file__).parent.parent.parent
    v5_data_path = root_dir / 'v5.0' / 'data' / 'topology_assignments.json'
    
    if v5_data_path.exists():
        with open(v5_data_path, 'r') as f:
            return json.load(f)
            
    raise FileNotFoundError("Topology assignments not found in v6.0/data or v5.0/data")

def load_knotinfo_path():
    """Returns path to knotinfo csv."""
    root_dir = Path(__file__).parent.parent.parent
    path = root_dir / 'data' / 'knotinfo_data_complete.csv'
    if not path.exists():
        # Fallback
        path = Path('../data/knotinfo_data_complete.csv')
    return path

def load_linkinfo_path():
    """Returns path to linkinfo csv."""
    root_dir = Path(__file__).parent.parent.parent
    path = root_dir / 'data' / 'linkinfo_data_complete.csv'
    if not path.exists():
        path = Path('../data/linkinfo_data_complete.csv')
    return path
