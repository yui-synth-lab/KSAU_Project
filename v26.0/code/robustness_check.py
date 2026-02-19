#!/usr/bin/env python3
"""
KSAU v26.0 Section 1 — Robustness and Sensitivity Check
======================================================
This script validates the stability of the Section 1 Two-Regime model
by varying the k_pivot and dk parameters.
"""

import sys
import os
import json
import numpy as np
from pathlib import Path

# Path setup
BASE = Path("E:/Obsidian/KSAU_Project")
sys.path.insert(0, str(BASE / "v26.0" / "code"))
from section_1_two_regime_scaling import TwoRegimeEngine

def run_sensitivity():
    engine = TwoRegimeEngine()
    
    k_pivots = [0.3, 0.35, 0.4, 0.45, 0.5]
    dks = [0.01, 0.05, 0.1]
    
    results = []
    print(f"{'k_pivot':<8} | {'dk':<6} | {'MAE':<8} | {'Chi2':<8}")
    print("-" * 40)
    
    for kp in k_pivots:
        for dk in dks:
            engine.k_pivot = kp
            engine.dk = dk
            
            # Global fit
            global_fit = engine.run_global_fit()
            # LOO-CV
            loo = engine.run_loo_cv()
            
            results.append({
                "k_pivot": kp,
                "dk": dk,
                "mae": loo["mae_all"],
                "chi2": global_fit["chi2"]
            })
            print(f"{kp:<8.2f} | {dk:<6.2f} | {loo['mae_all']:<8.4f} | {global_fit['chi2']:<8.4f}")

    # Find optimal kp/dk
    best = min(results, key=lambda x: x["mae"])
    print(f"\nOptimal from Scan: k_pivot={best['k_pivot']:.2f}, dk={best['dk']:.2f} (MAE={best['mae']:.4f})")
    
    out_path = BASE / "v26.0" / "data" / "robustness_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Robustness results saved to {out_path}")

if __name__ == "__main__":
    run_sensitivity()
