"""
KSAU v14.0.2 Gauge Coupling Formalization
Script purpose: Unified calculation of Weak, EM, and Strong couplings.
Dependencies: numpy, json
SSoT sources: v6.0/data/physical_constants.json
Author: Gemini (Simulation Kernel)
Date: 2026-02-16
"""

import numpy as np
import json
from pathlib import Path

def load_constants():
    """Load physical constants from SSoT with fallback."""
    path = Path(__file__).parent.parent.parent / 'v6.0' / 'data' / 'physical_constants.json'
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        try:
            path = Path('v6.0/data/physical_constants.json')
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'kappa': np.pi/24.0}

def coupling_constant_formalism():
    """
    KSAU v14.0: Gauge Coupling Formalization (Integrity Revision).
    Unifies alpha to kappa/18 and clarifies empirical fits.
    """
    consts = load_constants()
    kappa = consts['kappa']
    
    print("="*80)
    print(f"{'KSAU v14.0: Unified Gauge Couplings (Integrity Revision)':^80}")
    print("="*80)

    # 1. Weak Sector (Weinberg Angle)
    sin2w_pred = 1 - np.exp(-2 * kappa)
    sin2w_exp = 0.23122
    print(f"1. WEAK SECTOR (sin^2 theta_W):")
    print(f"   Formula  : 1 - exp(-2*kappa)")
    print(f"   Predicted: {sin2w_pred:.5f}")
    print(f"   Observed : {sin2w_exp:.5f} (Mz scale)")
    print(f"   Error    : {(sin2w_pred - sin2w_exp)/sin2w_exp*100:.2f}%")
    print()

    # 2. EM Sector (Fine Structure Constant)
    alpha_pred = kappa / 18.0
    alpha_exp = 1/137.036
    print(f"2. EM SECTOR (Fine Structure Constant alpha):")
    print(f"   Formula  : kappa / 18")
    print(f"   Predicted: {alpha_pred:.7f} (1/{1/alpha_pred:.3f})")
    print(f"   Observed : {alpha_exp:.7f} (1/{1/alpha_exp:.3f})")
    print(f"   Error    : {(alpha_pred - alpha_exp)/alpha_exp*100:.2f}%")
    print()

    # 3. Strong Sector (alpha_s)
    screening_factor = 0.90 
    alpha_s_pred = kappa * screening_factor
    alpha_s_exp = 0.118
    print(f"3. STRONG SECTOR (alpha_s at Mz):")
    print(f"   Formula  : kappa * 0.90 (Phenomenological Fit)")
    print(f"   Predicted: {alpha_s_pred:.4f}")
    print(f"   Observed : {alpha_s_exp:.4f}")
    print(f"   Error    : {(alpha_s_pred - alpha_s_exp)/alpha_s_exp*100:.2f}%")
    print("-" * 80)
    print("Note: All predictions are considered 'Bare' or 'Reference' values.")
    print("="*80)

if __name__ == "__main__":
    coupling_constant_formalism()
