#!/usr/bin/env python3
"""
KSAU v30.0 - LSS Coherence Check (Session 7 Fix)
================================================
Checks the ratio between the BAO scale (Mpc) and the Leech Lattice Radius (dimensionless).

SSoT Compliance:
- Loads R_cell and bao_sound_horizon_mpc from JSON.
"""

import numpy as np
import json
from pathlib import Path

def load_data():
    base_path = Path(__file__).resolve().parent.parent.parent
    with open(base_path / "v6.0" / "data" / "cosmological_constants.json", "r") as f:
        cosmo = json.load(f)
    with open(base_path / "v6.0" / "data" / "physical_constants.json", "r") as f:
        phys = json.load(f)
    return cosmo, phys

def check_ratio():
    cosmo, phys = load_data()

    # R_cell (Effective, dimensionless) from SSoT
    r_eff = cosmo["R_cell"]

    # Calculate R_pure (Fundamental) — SSoT: N_leech from physical_constants.json
    n_leech = phys["N_leech"]
    r_pure = n_leech**0.25
    
    # BAO Scale (Mpc) from SSoT
    bao_target = cosmo["bao_sound_horizon_mpc"]
    
    print(f"R_lattice (Pure): {r_pure:.4f}")
    print(f"R_lattice (Effective): {r_eff:.4f}")
    print(f"BAO Scale (Target): {bao_target} Mpc")
    
    print("\n--- Checking Pure Radius Ratio ---")
    ratio_pure = bao_target / r_pure
    print(f"Ratio (BAO / R_pure): {ratio_pure:.5f}")
    
    candidates = {
        "7 (Compact Dim)": 7.0,
        "e^2": np.e**2,
        "22/3": 22/3
    }
    
    best_fit = None
    min_diff = 1.0
    
    for name, val in candidates.items():
        diff = abs(ratio_pure - val) / val
        print(f"  vs {name} ({val:.5f}): Diff = {diff:.2%}")
        if diff < min_diff:
            min_diff = diff
            best_fit = (name, val)
            
    print(f"Best Fit (Pure): {best_fit[0]}")

if __name__ == "__main__":
    check_ratio()
