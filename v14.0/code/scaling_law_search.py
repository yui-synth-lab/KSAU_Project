"""
KSAU v14.0.2 Scaling Law Search
Script purpose: Scans the exponent space to find the best-fit hierarchy partition.
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

def find_correct_scaling_law():
    """
    Search for a monotonic exponent k that aligns g=2 with the GUT scale.
    Confirmed: k=4 aligns with spacetime dimension d=4.
    """
    consts = load_constants()
    
    # Constants
    X = 16.4 * np.pi 
    ln_mpl_mev = np.log(1.2209e22) 
    
    print("="*80)
    print(f"{'KSAU v14.0.2: Exponent Search for Hierarchy Partition':^80}")
    print("="*80)
    
    k_vals = [1, 2, 3, 4, 5, 6]
    
    for k in k_vals:
        val_2 = (2/3.0)**k
        m_2_pred = np.exp(ln_mpl_mev - X * val_2)
        print(f"  Exponent k={k:<2} | f(2)={val_2:.4f} | Mass(g=2) = {m_2_pred/1000/1e12:.2e} TeV")
        
        if 1e14 < m_2_pred/1000 < 1e16:
            print(f"    -> OPTIMAL FIT FOR GUT SCALE DETECTED (k={k})")

    print("="*80)

if __name__ == "__main__":
    find_correct_scaling_law()
