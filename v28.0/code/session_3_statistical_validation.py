import sys
import os
import json
import numpy as np
from pathlib import Path
from itertools import permutations
import time

# Add current code dir to path
sys.path.append(str(Path(__file__).parent))
from ksau_standard_cosmology import KSAUStandardCosmology

def run_validation():
    engine = KSAUStandardCosmology()
    
    # 7 Surveys Data (S8_obs is the value at z=0 or effective z=0)
    # Data source: wl5_survey_config.json and cmb_lensing_benchmarks.json
    surveys = {
        "DES Y3":      {"z": 0.33, "k": 0.15, "S8": 0.759, "err": 0.025},
        "CFHTLenS":    {"z": 0.40, "k": 0.20, "S8": 0.748, "err": 0.066},
        "DLS":         {"z": 0.52, "k": 0.22, "S8": 0.818, "err": 0.053},
        "HSC Y3":      {"z": 0.60, "k": 0.35, "S8": 0.776, "err": 0.033},
        "KiDS-Legacy": {"z": 0.26, "k": 0.70, "S8": 0.815, "err": 0.021},
        "Planck_PR4":  {"z": 2.00, "k": 0.07, "S8": 0.832, "err": 0.025},
        "ACT_DR6":     {"z": 1.70, "k": 0.07, "S8": 0.840, "err": 0.028}
    }
    
    survey_names = list(surveys.keys())
    z_vals = np.array([surveys[n]["z"] for n in survey_names])
    k_vals = np.array([surveys[n]["k"] for n in survey_names])
    s8_obs = np.array([surveys[n]["S8"] for n in survey_names])
    s8_err = np.array([surveys[n]["err"] for n in survey_names])
    
    def calc_chi2(ks, zs, obs, err):
        chi2 = 0
        for i in range(len(ks)):
            pred = engine.predict_s8_z0(ks[i], zs[i])
            chi2 += ((pred - obs[i]) / err[i])**2
        return float(chi2)

    # 1. Baseline
    baseline_chi2 = calc_chi2(k_vals, z_vals, s8_obs, s8_err)
    print("Baseline Chi2: {:.4f}".format(baseline_chi2))
    
    print("\nBaseline Individual Results:")
    for i, name in enumerate(survey_names):
        pred = engine.predict_s8_z0(k_vals[i], z_vals[i])
        tension = (pred - s8_obs[i]) / s8_err[i]
        print("{:12}: Pred={:.4f}, Obs={:.4f}, Tension={:.3f} sigma".format(name, pred, s8_obs[i], tension))

    # 2. Permutation Test
    print("\nRunning Permutation Test (5040)...")
    start_time = time.time()
    
    kz_pairs = list(zip(k_vals, z_vals))
    all_perms = list(permutations(kz_pairs))
    
    perm_chi2s = []
    for p in all_perms:
        pk = [x[0] for x in p]
        pz = [x[1] for x in p]
        chi2 = calc_chi2(pk, pz, s8_obs, s8_err)
        perm_chi2s.append(chi2)
    
    perm_chi2s = np.array(perm_chi2s)
    p_value_perm = np.sum(perm_chi2s <= baseline_chi2 * 1.000001) / len(perm_chi2s)
    
    print("Permutation Test p-value: {:.6f}".format(p_value_perm))
    print("Elapsed: {:.2f}s".format(time.time() - start_time))

    # 3. Bootstrap
    print("\nRunning Bootstrap (10000)...")
    start_time = time.time()
    
    num_bootstrap = 10000
    boot_chi2s = []
    
    for _ in range(num_bootstrap):
        s8_boot = np.random.normal(s8_obs, s8_err)
        chi2 = calc_chi2(k_vals, z_vals, s8_boot, s8_err)
        boot_chi2s.append(chi2)
        
    boot_chi2s = np.array(boot_chi2s)
    print("Bootstrap Mean Chi2: {:.4f}".format(np.mean(boot_chi2s)))
    print("Elapsed: {:.2f}s".format(time.time() - start_time))

    # Save
    results = {
        "baseline": {"chi2": baseline_chi2},
        "permutation_test": {"p_value": float(p_value_perm), "total": len(all_perms)},
        "bootstrap": {"mean_chi2": float(np.mean(boot_chi2s)), "iterations": num_bootstrap}
    }
    with open("v28.0/data/session_3_statistical_results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    run_validation()
