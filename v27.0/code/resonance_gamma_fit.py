#!/usr/bin/env python3
"""
KSAU v27.0 Session 2 — Resonance Gamma(k) Model
=====================================================
Derives R_cell from Leech lattice first principles:
R_cell = (N_leech)^(1/4) / (1 + alpha_ksau * beta_ksau)
k_res = 1 / R_cell

Model: gamma(k) = g_peak * exp(-(ln(k/k_res))^2 / (2*sigma^2)) + g_asym
This ensures gamma -> g_asym (near 0) for k -> 0 (GR return).
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

class ResonanceEngine:
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
        
        # 1. First-Principles R_cell Derivation
        self.n_leech = 196560
        self.alpha = 1.0 / 48.0
        self.beta = 13.0 / 6.0
        # R_cell = N^(1/4) / (1 + alpha*beta)
        self.r_cell_derived = (self.n_leech**0.25) / (1.0 + self.alpha * self.beta)
        self.k_res = 1.0 / self.r_cell_derived
        
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
        # params: [alpha, g_peak, sigma, g_asym, k_gr]
        g_peak, sigma, g_asym = params[1], params[2], params[3]
        k_gr = 0.001 # Fixed small scale for GR return to avoid parameter explosion
        gr_return = k / (k + k_gr)
        return (g_peak * np.exp(-(np.log(k / self.k_res))**2 / (2 * sigma**2)) + g_asym) * gr_return

    def compute_rz(self, k, z, params):
        alpha_param = params[0]
        g = self.gamma_k(k, params)
        r0 = self.r_base_3 * alpha_param * k**(-g)
        return r0 * (1.0 + z)**(-self.beta_fixed)

    def cost_function(self, params, training_data):
        alpha_param = params[0]
        if alpha_param <= 0: return 1e10
        
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
        # Params: [alpha, g_peak, sigma, g_asym]
        x0 = [1.0, 5.0, 1.5, -0.9] 
        bounds = [(0.1, 100.0), (0.0, 20.0), (0.1, 5.0), (-2.0, 1.0)]
        res = minimize(self.cost_function, x0, args=(self.all_data,), method="L-BFGS-B", bounds=bounds)
        return res

def main():
    engine = ResonanceEngine()
    print(f"R_cell Derived (Leech First Principles): {engine.r_cell_derived:.4f} Mpc/h")
    print(f"k_res Derived: {engine.k_res:.4f} h/Mpc")
    print("-" * 40)
    print("Running Resonance-Dependent Gamma Fit (WL + CMB Lensing)...")
    res = engine.fit()
    
    if res.success:
        p = res.x
        print(f"  Alpha      : {p[0]:.4f}")
        print(f"  Gamma Peak : {p[1]:.4f} (at k = k_res)")
        print(f"  Sigma      : {p[2]:.4f} (log-width)")
        print(f"  Gamma Asym : {p[3]:.4f} (at k -> 0/inf)")
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
            "r_cell_derived": engine.r_cell_derived,
            "k_res_derived": engine.k_res,
            "params": p.tolist(),
            "chi2": res.fun,
            "per_survey": per_survey
        }
        with open(BASE / "v27.0" / "data" / "resonance_fit_results.json", "w") as f:
            json.dump(output, f, indent=2)
    else:
        print("Fit failed!")

if __name__ == "__main__":
    main()
