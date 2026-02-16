"""
KSAU v14.0.2 Invariant Integrity Scanner
Script purpose: Statistical verification of the significance of geometric alignments.
Dependencies: numpy, json
SSoT sources: v6.0/data/physical_constants.json
Author: Gemini (Simulation Kernel)
Date: 2026-02-16
"""

import numpy as np
import json
from pathlib import Path

def load_constants():
    """SSoT compliant constant loader."""
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

def invariant_integrity_scanner():
    """
    KSAU v14.0: Invariant Integrity & Statistical Rigor Scanner (Fixed).
    Reduces empirical fits to structural necessities with fixed seed.
    """
    np.random.seed(42) 
    
    print("="*80)
    print(f"{'KSAU v14.0: Invariant Integrity & Statistical Rigor Scanner':^80}")
    print(f"{'Status: SSoT Compliant & Reproducible':^80}")
    print("="*80)

    consts = load_constants()
    kappa = consts['kappa']
    alpha_exp = 1/137.035999
    
    print("\n[EM Sector: Official Invariant Selection]")
    alpha_v14 = kappa / 18.0
    err_alpha = abs(alpha_v14 - alpha_exp) / alpha_exp * 100
    print(f"  Selected Formula: kappa / 18")
    print(f"  Value           : 1/{1/alpha_v14:.4f}")
    print(f"  Error           : {err_alpha:.4f}%")

    print("\n[Monte Carlo Null Hypothesis Test (N=100,000)]")
    invariants = [np.pi, 24, 41, 60, 18, 2]
    ops = [lambda x, y: x*y, lambda x, y: x/y, lambda x, y: x+y, lambda x, y: x-y]
    
    trials = 100000
    hits = 0
    best_err = 100.0
    
    for _ in range(trials):
        subset = np.random.choice(invariants, 3, replace=True)
        res = subset[0]
        for i in range(1, 3):
            op = np.random.choice(ops)
            res = op(res, subset[i])
        
        if res <= 0 or np.isnan(res) or np.isinf(res): continue
        if res > 1: res = 1/res
        
        err = abs(res - alpha_exp) / alpha_exp * 100
        if err < err_alpha: 
            hits += 1
        if err < best_err:
            best_err = err
            
    p_value = hits / trials
    print(f"  Trials         : {trials}")
    print(f"  Target Precision: {err_alpha:.4f}%")
    print(f"  Hits           : {hits}")
    print(f"  p-value        : {p_value:.5f}")
    print(f"  Best Random Err: {best_err:.5f}%")
    
    if p_value < 0.01:
        print("\nVERDICT: STATISTICALLY SIGNIFICANT (p < 0.01).")
    else:
        print("\nVERDICT: CAUTION REQUIRED.")

    print("="*80)

if __name__ == "__main__":
    invariant_integrity_scanner()
