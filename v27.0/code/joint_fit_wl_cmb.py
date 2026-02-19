#!/usr/bin/env python3
"""
KSAU v27.0 Session 1 — Joint Fit: Low-z WL + High-z CMB Lensing
==============================================================
Model: R₀(k, z) = R_base(3) * alpha * k^(-gamma) * (1+z)^(-beta)
Fits alpha and gamma to both low-z surveys and Planck PR4 lensing.
"""

import sys
import os
import json
import numpy as np
from pathlib import Path
from scipy.optimize import minimize
from scipy.interpolate import RegularGridInterpolator

# Path setup
BASE = Path("E:/Obsidian/KSAU_Project")
sys.path.insert(0, str(BASE / "v23.0" / "code"))
from loo_cv_engine_v23_final_audit import LOOCVFinalAudit

# SSoT Paths
SSOT_DIR = BASE / "v6.0" / "data"
COSMO_CONFIG = SSOT_DIR / "cosmological_constants.json"
PHYS_CONSTANTS = SSOT_DIR / "physical_constants.json"
WL5_CONFIG = SSOT_DIR / "wl5_survey_config.json"
CMB_BENCHMARK = BASE / "v27.0" / "data" / "cmb_lensing_benchmarks.json"

class JointFitEngine:
    def __init__(self):
        with open(PHYS_CONSTANTS, "r", encoding="utf-8") as f:
            self.phys = json.load(f)
        with open(COSMO_CONFIG, "r", encoding="utf-8") as f:
            self.cosmo = json.load(f)
        with open(WL5_CONFIG, "r", encoding="utf-8") as f:
            self.wl_surveys = json.load(f)["surveys"]
        with open(CMB_BENCHMARK, "r", encoding="utf-8") as f:
            self.cmb_benchmarks = json.load(f)["benchmarks"]
        
        self.ksau = LOOCVFinalAudit(config_path=str(COSMO_CONFIG))
        
        self.kappa = self.phys["kappa"]
        self.r_base_3 = 3.0 / (2.0 * self.kappa)
        self.beta_fixed = self.cosmo["beta_ssot"]
        self.growth_index = self.cosmo["scaling_laws"]["growth_index"]
        self.rz_min = self.cosmo["scaling_laws"]["rz_min"]
        self.rz_max = self.cosmo["scaling_laws"]["rz_max"]
        
        # Merge datasets for joint fit
        self.all_data = {}
        for name, sv in self.wl_surveys.items():
            self.all_data[name] = {
                "k_eff": sv["k_eff"],
                "z_eff": sv["z_eff"],
                "S8_obs_z0": sv["S8_obs"],
                "S8_err_z0": sv["S8_err"]
            }
        
        # Add Planck PR4 Lensing (High-z anchor)
        pr4 = self.cmb_benchmarks["Planck_PR4_Lensing"]
        self.all_data["Planck_PR4"] = {
            "k_eff": 0.07, # k_eff for PR4
            "z_eff": pr4["z_eff"],
            "S8_obs_z0": pr4["S8_z0"],
            "S8_err_z0": pr4["S8_err"]
        }
        
        self.interp = self._build_s8_interpolator()

    def _build_s8_interpolator(self):
        # Need a grid covering z=0 to z=2.0
        z_vals = np.linspace(0, 2.0, 10)
        rz_grid = np.logspace(np.log10(self.rz_min), np.log10(self.rz_max), 100)
        s8_grid = np.zeros((len(rz_grid), len(z_vals)))
        
        for j, z in enumerate(z_vals):
            for i, rz in enumerate(rz_grid):
                s8_grid[i, j] = self.ksau.predict_s8_z(z, rz, 0.0, use_nl=True)
        
        return RegularGridInterpolator(
            (np.log(rz_grid), z_vals),
            s8_grid,
            method="linear",
            bounds_error=False,
            fill_value=None 
        )

    def s8_query(self, rz, z):
        res = self.interp([[np.log(max(rz, 1e-5)), z]])[0]
        return float(res)

    def compute_rz(self, k, z, params):
        alpha, gamma = params
        r0 = self.r_base_3 * alpha * k**(-gamma)
        return r0 * (1.0 + z)**(-self.beta_fixed)

    def cost_function(self, params, training_data):
        alpha, gamma = params
        if alpha <= 0: return 1e10 + abs(alpha)*1e6
        
        chi2 = 0.0
        for name, sv in training_data.items():
            k, z = sv["k_eff"], sv["z_eff"]
            rz = self.compute_rz(k, z, params)
            rz = np.clip(rz, self.rz_min, self.rz_max)
            
            s8_pred_z = self.s8_query(rz, z)
            
            # Translate pred back to z=0 for comparison with S8_obs_z0
            a = 1.0 / (1.0 + z)
            s8_pred_z0 = s8_pred_z / (a**self.growth_index)
            
            chi2 += ((s8_pred_z0 - sv["S8_obs_z0"]) / sv["S8_err_z0"])**2
        return chi2

    def fit(self):
        res = minimize(
            self.cost_function,
            [7.7, -0.9], # Starting from v26.0 values
            args=(self.all_data,),
            method="L-BFGS-B",
            bounds=[(0.1, 100.0), (-5.0, 5.0)]
        )
        return res

def main():
    engine = JointFitEngine()
    print("Running Joint Fit (WL + CMB Lensing)...")
    res = engine.fit()
    
    if res.success:
        alpha_opt, gamma_opt = res.x
        print(f"  Alpha: {alpha_opt:.4f}")
        print(f"  Gamma: {gamma_opt:.4f}")
        print(f"  Chi2:  {res.fun:.4f} (for {len(engine.all_data)} points)")
        
        # Per-survey report
        per_survey = {}
        for name, sv in engine.all_data.items():
            rz = engine.compute_rz(sv["k_eff"], sv["z_eff"], res.x)
            s8_pred_z = engine.s8_query(rz, sv["z_eff"])
            a = 1.0 / (1.0 + sv["z_eff"])
            s8_pred_z0 = s8_pred_z / (a**engine.growth_index)
            tension = (s8_pred_z0 - sv["S8_obs_z0"]) / sv["S8_err_z0"]
            per_survey[name] = {
                "z": sv["z_eff"],
                "k": sv["k_eff"],
                "rz": round(rz, 3),
                "s8_obs": sv["S8_obs_z0"],
                "s8_pred_eff_z0": round(s8_pred_z0, 4),
                "tension": round(tension, 3)
            }
            print(f"    {name:<12}: Tension = {tension:>+6.2f} sigma | rz = {rz:>6.2f}")
            
        output = {
            "alpha": alpha_opt,
            "gamma": gamma_opt,
            "chi2": res.fun,
            "per_survey": per_survey
        }
        
        out_path = BASE / "v27.0" / "data" / "joint_fit_results.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
        print(f"Results saved to {out_path}")
    else:
        print("Fit failed!")

if __name__ == "__main__":
    main()
