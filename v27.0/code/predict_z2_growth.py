#!/usr/bin/env python3
import sys
import os
import json
import numpy as np
from pathlib import Path

# Path setup
BASE = Path("E:/Obsidian/KSAU_Project")
sys.path.insert(0, str(BASE / "v23.0" / "code"))
from loo_cv_engine_v23_final_audit import LOOCVFinalAudit

# SSoT Paths
SSOT_DIR = BASE / "v6.0" / "data"
COSMO_CONFIG = SSOT_DIR / "cosmological_constants.json"
PHYS_CONSTANTS = SSOT_DIR / "physical_constants.json"

def predict_z2():
    # Load Constants
    with open(PHYS_CONSTANTS, "r", encoding="utf-8") as f:
        phys = json.load(f)
    with open(COSMO_CONFIG, "r", encoding="utf-8") as f:
        cosmo = json.load(f)
    
    # KSAU Engine
    engine = LOOCVFinalAudit(config_path=str(COSMO_CONFIG))
    
    # v26.0 Section 1 Parameters
    alpha = 7.7229
    gamma = -0.9283
    beta = cosmo["beta_ssot"]
    kappa = phys["kappa"]
    r_base_3 = 3.0 / (2.0 * kappa)
    
    # Planck PR4 Lensing Benchmark
    z_target = 2.0
    k_target = 0.07
    s8_obs_z0 = 0.832
    s8_err_z0 = 0.025
    
    # Compute Rz at z=2
    r0 = r_base_3 * alpha * k_target**(-gamma)
    rz = r0 * (1.0 + z_target)**(-beta)
    
    print(f"Prediction for z={z_target}, k={k_target}:")
    print(f"  R0(k) : {r0:.4f}")
    print(f"  Rz    : {rz:.4f}")
    
    # Predict S8 at z=2 using KSAU Engine
    s8_pred_z = engine.predict_s8_z(z_target, rz, 0.0, use_nl=True)
    print(f"  S8_pred(z=2) : {s8_pred_z:.4f}")
    
    # Translate back to S8_z0 using standard growth index gamma=0.55
    # S8(z) = S8(0) * a^0.55 => S8(0) = S8(z) / a^0.55
    a = 1.0 / (1.0 + z_target)
    growth_index = cosmo["scaling_laws"]["growth_index"]
    s8_pred_z0 = s8_pred_z / (a**growth_index)
    
    print(f"  S8_pred(z=0) : {s8_pred_z0:.4f} (Effective)")
    print(f"  Benchmark    : {s8_obs_z0:.4f} +/- {s8_err_z0:.4f}")
    
    tension = (s8_pred_z0 - s8_obs_z0) / s8_err_z0
    print(f"  Tension      : {tension:.3f} sigma")
    
    # Save results
    res = {
        "z": z_target,
        "k": k_target,
        "alpha": alpha,
        "gamma": gamma,
        "rz": rz,
        "s8_pred_z": s8_pred_z,
        "s8_pred_z0_eff": s8_pred_z0,
        "benchmark_s8_z0": s8_obs_z0,
        "benchmark_s8_err": s8_err_z0,
        "tension": tension
    }
    
    out_path = BASE / "v27.0" / "data" / "z2_prediction_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
    print(f"Results saved to {out_path}")

if __name__ == "__main__":
    predict_z2()
