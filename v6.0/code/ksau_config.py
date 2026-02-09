import numpy as np
import json
from pathlib import Path

# ============================================================================
# THEORETICAL CONSTANTS (The Laws of KSAU)
# ============================================================================
KAPPA = np.pi / 24
ALPHA_GEOM = np.pi / 432
PI_SHIFT = np.pi

# Intercept Defaults (Theoretical origins)
BQ_DEFAULT = -(7 + 7 * KAPPA)
CL_DEFAULT = KAPPA - (7/3) * (1 + KAPPA)

def get_kappa_coeffs():
    """
    Returns the coefficients for the Holographic Dual Mass Formulas.
    Slopes are derived geometrically from Spacetime Dimensions and Topology Bases.
    """
    phys = load_physical_constants()
    
    # 1. Base Constants
    G = phys['G_catalan']
    
    # 2. Dimensions
    dim_bulk = phys['dimensions']['bulk_compact'] # 7
    dim_boundary = phys['dimensions']['boundary_projection'] # 9
    
    # 3. Topology Bases
    base_q = phys['topology_bases']['quark_components'] # 10
    base_l = phys['topology_bases']['lepton_components'] # 2
    
    # 4. Geometric Derivation of Slopes
    # Quark Slope = (base_q / dim_bulk) * G  => (10/7) * G approx 10 * kappa
    quark_slope = (base_q / dim_bulk) * G
    
    # Lepton Slope = (base_l / dim_boundary) * G => (2/9) * G approx 14/9 * kappa
    lepton_slope = (base_l / dim_boundary) * G
    
    return {
        'quark_vol_coeff': quark_slope,
        'quark_intercept': BQ_DEFAULT,
        'lepton_n2_coeff': lepton_slope,
        'lepton_intercept': CL_DEFAULT
    }

# For backward compatibility with scripts using LEPTON_GAMMA
# We derive it using the nominal theoretical values
LEPTON_GAMMA = (2/9) * 0.915965594177219 # (2/9) * G


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

def get_unified_particle_data():
    """
    Merges topology invariants (assignments) with physical constants (mass, gen).
    This centralizes data and removes redundancy between the two JSON files.
    """
    phys = load_physical_constants()
    
    # Base assignments (invariants like volume, crossing_number)
    v6_data_path = Path(__file__).parent.parent / 'data' / 'topology_assignments.json'
    if not v6_data_path.exists():
        raise FileNotFoundError("Topology assignments not found.")
    
    with open(v6_data_path, 'r') as f:
        assignments = json.load(f)

    # Merge physical metadata into assignments
    # We look into quarks, leptons, and bosons sections of physical_constants.json
    for sector in ['quarks', 'leptons', 'bosons']:
        if sector not in phys: continue
        for p_name, p_meta in phys[sector].items():
            if not isinstance(p_meta, dict): continue # Skip 'scaling' key
            if p_name in assignments:
                # Update assignment with mass and other metadata if not already present
                # or to ensure latest PDG values from physical_constants override
                assignments[p_name].update(p_meta)
    
    return assignments

def load_topology_assignments():
    """Loads topology assignments (unified with physical constants)."""
    return get_unified_particle_data()

def load_knotinfo_path():
    root_dir = Path(__file__).parent.parent.parent
    return root_dir / 'data' / 'knotinfo_data_complete.csv'

def load_linkinfo_path():
    root_dir = Path(__file__).parent.parent.parent
    return root_dir / 'data' / 'linkinfo_data_complete.csv'
