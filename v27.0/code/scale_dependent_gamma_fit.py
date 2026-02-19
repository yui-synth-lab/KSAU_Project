#!/usr/bin/env python3
"""
KSAU v27.0 Session 1 — Scale-Dependent Gamma(k) Model
=====================================================
Model: R₀(k, z) = R_base(3) * alpha * k^(-gamma(k)) * (1+z)^(-beta)
where gamma(k) = gamma_low if k < k_pivot else gamma_high.
Smooth transition: gamma(k) = gamma_high + (gamma_low - gamma_high) / (1 + (k/k_pivot)**n)
"""

import sys
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

class ScaleDepEngine:
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
        
        self.all_data = {}
        for name, sv in self.wl_surveys.items():
            self.all_data[name] = {
                "k_eff": sv["k_eff"], "z_eff": sv["z_eff"],
                "S8_obs_z0": sv["S8_obs"], "S8_err_z0": sv["S8_err"]
            }
        pr4 = self.cmb_benchmarks["Planck_PR4_Lensing"]
        self.all_data["Planck_PR4"] = {
            "k_eff": pr4["k_eff"], "z_eff": pr4["z_eff"],
            "S8_obs_z0": pr4["S8_z0"], "S8_err_z0": pr4["S8_err"]
        }
        
        # Add ACT-DR6 as well
        act = self.cmb_benchmarks["ACT_DR6_Lensing"]
        self.all_data["ACT_DR6"] = {
            "k_eff": act["k_eff"], "z_eff": act["z_eff"],
            "S8_obs_z0": act["S8_z0"], "S8_err_z0": act["S8_err"]
        }

        self.interp = self._build_s8_interpolator()

    def _build_s8_interpolator(self):
        z_vals = np.linspace(0, 2.0, 10)
        rz_grid = np.logspace(np.log10(self.rz_min), np.log10(self.rz_max), 100)
        s8_grid = np.zeros((len(rz_grid), len(z_vals)))
        for j, z in enumerate(z_vals):
            for i, rz in enumerate(rz_grid):
                s8_grid[i, j] = self.ksau.predict_s8_z(z, rz, 0.0, use_nl=True)
        return RegularGridInterpolator((np.log(rz_grid), z_vals), s8_grid, method="linear", bounds_error=False, fill_value=None)

    def s8_query(self, rz, z):
        res = self.interp([[np.log(max(rz, 1e-5)), z]])[0]
        return float(res)

    def gamma_k(self, k, params):
        g_low, g_high, k_pivot = params[1], params[2], params[3]
        n = 4.0 # Steepness of transition
        return g_high + (g_low - g_high) / (1.0 + (k / k_pivot)**n)

    def compute_rz(self, k, z, params):
        alpha = params[0]
        g = self.gamma_k(k, params)
        r0 = self.r_base_3 * alpha * k**(-g)
        return r0 * (1.0 + z)**(-self.beta_fixed)

    def cost_function(self, params, training_data):
        alpha = params[0]
        if alpha <= 0: return 1e10
        
        chi2 = 0.0
        for name, sv in training_data.items():
            rz = self.compute_rz(sv["k_eff"], sv["z_eff"], params)
            rz = np.clip(rz, self.rz_min, self.rz_max)
            s8_pred_z = self.s8_query(rz, sv["z_eff"])
            a = 1.0 / (1.0 + sv["z_eff"])
            s8_pred_z0 = s8_pred_z / (a**self.growth_index)
            chi2 += ((s8_pred_z0 - sv["S8_obs_z0"]) / sv["S8_err_z0"])**2
        return chi2

    def fit(self):
        # Params: [alpha, gamma_low, gamma_high, k_pivot]
        # Use SSoT k_flip_scale as initial guess for k_pivot
        k_init = self.cosmo.get("k_flip_scale", 0.058)
        x0 = [7.0, 5.0, -0.9, k_init] 
        bounds = [(0.1, 100.0), (-5.0, 10.0), (-5.0, 5.0), (0.01, 0.5)]
        res = minimize(self.cost_function, x0, args=(self.all_data,), method="L-BFGS-B", bounds=bounds)
        return res

def main():
    engine = ScaleDepEngine()
    print("Running Scale-Dependent Gamma Fit (WL + CMB Lensing)...")
    res = engine.fit()
    
    if res.success:
        p = res.x
        print(f"  Alpha      : {p[0]:.4f}")
        print(f"  Gamma_low  : {p[1]:.4f} (at k < k_pivot)")
        print(f"  Gamma_high : {p[2]:.4f} (at k > k_pivot)")
        print(f"  k_pivot    : {p[3]:.4f}")
        print(f"  Chi2       : {res.fun:.4f} (for {len(engine.all_data)} points)")
        
        per_survey = {}
        for name, sv in engine.all_data.items():
            rz = engine.compute_rz(sv["k_eff"], sv["z_eff"], p)
            g = engine.gamma_k(sv["k_eff"], p)
            s8_pred_z = engine.s8_query(rz, sv["z_eff"])
            a = 1.0 / (1.0 + sv["z_eff"])
            s8_pred_z0 = s8_pred_z / (a**engine.growth_index)
            tension = (s8_pred_z0 - sv["S8_obs_z0"]) / sv["S8_err_z0"]
            per_survey[name] = {
                "gamma": round(g, 3),
                "rz": round(rz, 3),
                "s8_pred_eff_z0": round(s8_pred_z0, 4),
                "tension": round(tension, 3)
            }
            print(f"    {name:<12}: Tension = {tension:>+6.2f} sigma | gamma = {g:>+6.2f} | rz = {rz:>6.2f}")
            
        output = {
            "params": p.tolist(),
            "chi2": res.fun,
            "per_survey": per_survey
        }
        with open(BASE / "v27.0" / "data" / "scale_dependent_fit_results.json", "w") as f:
            json.dump(output, f, indent=2)
    else:
        print("Fit failed!")

if __name__ == "__main__":
    main()
