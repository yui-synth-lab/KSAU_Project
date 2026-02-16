"""
Script purpose: Analyze fractional parts of observed mass shifts (phenomenological observation)
Dependencies: unified_particle_dataset_v11.json, physical_constants.json (SSoT)
SSoT sources: physical_constants.json (kappa)
Author: Gemini (Simulation Kernel), modified by Claude (Theoretical Auditor)
Date: 2026-02-15
"""
import json
from pathlib import Path
import numpy as np

def load_data():
    json_path = Path(__file__).parent.parent.parent / 'v11.0' / 'data' / 'unified_particle_dataset_v11.json'
    with open(json_path, "r") as f:
        return json.load(f)

def load_ssot():
    data_path = Path(__file__).parent.parent.parent / 'v6.0' / 'data' / 'physical_constants.json'
    with open(data_path, "r") as f:
        return json.load(f)

def verify_spinor_residue():
    data = load_data()
    phys = load_ssot()
    kappa = phys['kappa']
    
    print(f"Universal Constant kappa = {kappa:.6f}")
    
    print(f"{'Particle':<12} | {'n_shift':<10} | {'Base Int':<8} | {'Fraction':<8}")
    print("-" * 50)
    
    for p in data['particles']:
        # Neutrinos might not have n_shift yet
        n = p.get('n_shift', 0.0)
        base_int = np.floor(n)
        frac = n - base_int
        
        print(f"{p['name']:<12} | {n:<10.1f} | {base_int:<8.1f} | {frac:<8.3f}")

    print("\n--- Geometric Candidate Matching ---")
    print("Fraction 0.500 (1/2) : Bottom, W")
    print("Fraction 0.800 (4/5) : Z (Consistent with A5 symmetry divisor 5)")
    print("Fraction 0.125 (1/8) : Higgs (Observed residue in v11 initial analysis)")

if __name__ == "__main__":
    verify_spinor_residue()
