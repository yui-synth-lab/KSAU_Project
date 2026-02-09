import numpy as np
import json
from pathlib import Path

# ============================================================================
# THEORETICAL CONSTANTS (The Laws of KSAU)
# ============================================================================
KAPPA = np.pi / 24
ALPHA_GEOM = np.pi / 432

# Quark Parameters (Volume Law)
BQ_DEFAULT = -(7 + 7 * KAPPA)

# Lepton Parameters (Complexity Law)
# Cl = kappa - 7/3(1+kappa)
CL_DEFAULT = KAPPA - (7/3) * (1 + KAPPA)
LEPTON_GAMMA = (14/9) * KAPPA

def get_kappa_coeffs():
    """Returns the coefficients for the Holographic Dual Mass Formulas."""
    return {
        'quark_vol_coeff': 10 * KAPPA,
        'quark_intercept': BQ_DEFAULT,
        'lepton_n2_coeff': LEPTON_GAMMA,
        'lepton_intercept': CL_DEFAULT
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
    """Loads topology assignments."""
    v6_data_path = Path(__file__).parent.parent / 'data' / 'topology_assignments.json'
    if v6_data_path.exists():
        with open(v6_data_path, 'r') as f:
            return json.load(f)
    raise FileNotFoundError("Topology assignments not found.")

def load_knotinfo_path():
    root_dir = Path(__file__).parent.parent.parent
    return root_dir / 'data' / 'knotinfo_data_complete.csv'

def load_linkinfo_path():
    root_dir = Path(__file__).parent.parent.parent
    return root_dir / 'data' / 'linkinfo_data_complete.csv'
