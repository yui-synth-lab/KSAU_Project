#!/usr/bin/env python3
"""
KSAU v28.0 - SKC Validation Script
==================================
Verifies that the unified engine reproduces v27.0 results.
"""

import sys
import json
import numpy as np
from pathlib import Path

# Path setup
BASE = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE / "v28.0" / "code"))

from ksau_standard_cosmology import KSAUStandardCosmology

V27_DATA = BASE / "v27.0" / "data"
RESONANCE_FIT_RESULTS = V27_DATA / "resonance_fit_results.json"

def validate():
    engine = KSAUStandardCosmology()
    print("Starting SKC Validation (Reproduction of v27.0 Resonance Model)...")
    
    all_passed = True

    # 1. Validate S8 (Resonance Fit Results)
    if RESONANCE_FIT_RESULTS.exists():
        with open(RESONANCE_FIT_RESULTS, "r", encoding="utf-8") as f:
            v27_res = json.load(f)
        
        # Load survey configurations to get k_eff and z_eff for all 7 surveys
        with open(BASE / "v6.0" / "data" / "wl5_survey_config.json", "r", encoding="utf-8") as f:
            wl_cfg = json.load(f)["surveys"]
        with open(V27_DATA / "cmb_lensing_benchmarks.json", "r", encoding="utf-8") as f:
            cmb_cfg = json.load(f)["benchmarks"]

        survey_coords = {}
        for name, sv in wl_cfg.items():
            survey_coords[name] = (sv["k_eff"], sv["z_eff"])
        survey_coords["Planck_PR4"] = (cmb_cfg["Planck_PR4_Lensing"]["k_eff"], cmb_cfg["Planck_PR4_Lensing"]["z_eff"])
        survey_coords["ACT_DR6"] = (cmb_cfg["ACT_DR6_Lensing"]["k_eff"], cmb_cfg["ACT_DR6_Lensing"]["z_eff"])

        print("\nChecking S8 Resonance Model Reproduction (7 Surveys):")
        print(f"{'Survey':<15} | {'k_eff':<6} | {'z_eff':<6} | {'v27_pred':<10} | {'v28_pred':<10} | {'Tension':<8} | {'Status'}")
        print("-" * 85)
        
        for name in ["DES Y3", "CFHTLenS", "DLS", "HSC Y3", "KiDS-Legacy", "Planck_PR4", "ACT_DR6"]:
            data_v27 = v27_res["per_survey"][name]
            k, z = survey_coords[name]
            
            pred_v28 = engine.predict_s8_z0(k, z)
            pred_v27 = data_v27["s8_pred_eff_z0"]
            tension = data_v27["tension"]
            
            diff = abs(pred_v28 - pred_v27)
            # Higher precision required for reproduction; Tension check for physics validity
            repro_status = "PASS" if diff < 1e-3 else "FAIL"
            tension_status = "OK" if abs(tension) < 1.1 else "HIGH"
            
            print(f"  {name:<15} | {k:<6.2f} | {z:<6.2f} | {pred_v27:<10.4f} | {pred_v28:<10.4f} | {tension:>+7.2f} | {repro_status}")
            
            if repro_status == "FAIL": all_passed = False
            if tension_status == "HIGH":
                print(f"    WARNING: {name} tension is {tension:.2f} sigma (>= 1.1 sigma)")
                # DLS tension in resonance_fit_results.json is -1.029, so it should pass < 1.1
        
    else:
        print("\nSkipping S8 check (resonance_fit_results.json not found).")
        all_passed = False

    # 2. Validate H0 (Evolution Results)
    h0_results_path = V27_DATA / "h0_evolution_results.json"
    if h0_results_path.exists():
        with open(h0_results_path, "r", encoding="utf-8") as f:
            v27_h0 = json.load(f)
        
        print("\nChecking H0 Relaxation Model Reproduction:")
        h_ksau_v28 = engine.predict_h(0)
        h_ksau_v27 = v27_h0["h0_ksau_z0"]
        
        diff = abs(h_ksau_v28 - h_ksau_v27)
        status = "PASS" if diff < 1e-4 else "FAIL"
        print(f"  H0_KSAU(z=0)  : v27={h_ksau_v27:.4f}, v28={h_ksau_v28:.4f} | Diff={diff:.6f} | {status}")
        if status == "FAIL": all_passed = False
        
        # Check extrapolated H0 (SH0ES comparison)
        z_local = np.linspace(0.02, 0.15, 20)
        h_extrap_v28 = np.mean([engine.predict_h(z) / (engine.h_lcdm(z)/engine.h0_planck) for z in z_local])
        h_extrap_v27 = v27_h0["h0_sh0es_equivalent"]
        
        diff = abs(h_extrap_v28 - h_extrap_v27)
        status = "PASS" if diff < 1e-4 else "FAIL"
        print(f"  H0_SH0ES_equiv: v27={h_extrap_v27:.4f}, v28={h_extrap_v28:.4f} | Diff={diff:.6f} | {status}")
        if status == "FAIL": all_passed = False
    else:
        print("\nSkipping H0 check (v27.0 data not found).")

    print("\n" + "="*40)
    if all_passed:
        print("FINAL STATUS: SUCCESS - 100% Reproduction Confirmed.")
    else:
        print("FINAL STATUS: FAILURE - Discrepancies detected.")
    print("="*40)

    # Save validation results
    val_results = {
        "reproduction_success": all_passed,
        "timestamp": "2026-02-19"
    }
    with open(BASE / "v28.0" / "data" / "reproduction_validation.json", "w") as f:
        json.dump(val_results, f, indent=2)

if __name__ == "__main__":
    validate()
