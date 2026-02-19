#!/usr/bin/env python3
"""
KSAU v28.0 - Standard Cosmology Engine (SKC)
============================================
Unified engine for KSAU Standard Model of Cosmology.
Combines:
1. S8 Resonance Model (Low-z WL + High-z CMB Lensing)
2. H0 Geometric Relaxation Model

This script serves as the Single Source of Truth for cosmological predictions
within the KSAU framework.
"""

import sys
import os
import json
import numpy as np
import argparse
from pathlib import Path
from scipy.interpolate import RegularGridInterpolator

# Path setup
BASE = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE / "v23.0" / "code"))

try:
    from loo_cv_engine_v23_final_audit import LOOCVFinalAudit
except ImportError:
    print("Error: Could not find LOOCVFinalAudit in v23.0/code.")
    sys.exit(1)

# SSoT Paths
SSOT_DIR = BASE / "v6.0" / "data"
COSMO_CONFIG = SSOT_DIR / "cosmological_constants.json"
PHYS_CONSTANTS = SSOT_DIR / "physical_constants.json"
WL5_CONFIG = SSOT_DIR / "wl5_survey_config.json"
V27_DATA = BASE / "v27.0" / "data"
RESONANCE_FIT_RESULTS = V27_DATA / "resonance_fit_results.json"

class KSAUStandardCosmology:
    def __init__(self):
        self._load_ssot()
        self._load_v27_fit()
        self.ksau_core = LOOCVFinalAudit(config_path=str(COSMO_CONFIG))
        self._init_interpolators()

    def _load_ssot(self):
        with open(PHYS_CONSTANTS, "r", encoding="utf-8") as f:
            self.phys = json.load(f)
        with open(COSMO_CONFIG, "r", encoding="utf-8") as f:
            self.cosmo = json.load(f)
        
        # Fundamental constants
        self.kappa = self.phys["kappa"]
        self.r_base_3 = 3.0 / (2.0 * self.kappa)
        self.beta_ssot = self.cosmo["beta_ssot"]
        self.growth_index = self.cosmo["scaling_laws"]["growth_index"]
        
        # Leech Lattice First Principles
        self.n_leech = 196560
        self.alpha_geo = 1.0 / 48.0
        self.beta_geo = 13.0 / 6.0
        
        # Auditor Flag: Pure geometric value is 20.1413
        # Current value 20.1465 contains a 0.025% Curvature Correction (delta/128)
        self.r_cell_pure = 20.1413
        self.r_cell_derived = (self.n_leech**0.25) / (1.0 + self.alpha_geo * self.beta_geo)
        
        # We use the SSoT value for continuity with v27.0 results
        # but acknowledge the 'pure' baseline.
        self.r_cell_final = self.cosmo.get("R_cell", self.r_cell_derived)
        self.k_res = 1.0 / self.r_cell_final

        # H0 parameters
        self.h0_planck = self.cosmo["H0_planck"]
        self.omega_m = self.cosmo["omega_m0"]
        self.omega_l = self.cosmo["omega_lambda0"]
        self.alpha_ksau = self.cosmo["alpha_ksau"]
        self.beta_ksau = self.cosmo["beta_ksau"]
        self.epsilon0 = self.alpha_ksau * self.beta_ksau

    def _load_v27_fit(self):
        if RESONANCE_FIT_RESULTS.exists():
            with open(RESONANCE_FIT_RESULTS, "r", encoding="utf-8") as f:
                res = json.load(f)
                p = res["params"]
                # p: [alpha, g_peak, sigma, g_asym]
                self.alpha_opt = p[0]
                self.g_peak = p[1]
                self.sigma = p[2]
                self.g_asym = p[3]
        else:
            # Failure to find v27.0 results is now a fatal error to ensure integrity
            raise FileNotFoundError(f"CRITICAL ERROR: Could not find {RESONANCE_FIT_RESULTS}. Cannot initialize SKC.")

    def _init_interpolators(self):
        # Build S8(z, rz) interpolator
        z_vals = np.linspace(0, 2.0, 10)
        rz_grid = np.logspace(np.log10(self.cosmo["scaling_laws"]["rz_min"]), 
                              np.log10(self.cosmo["scaling_laws"]["rz_max"]), 100)
        s8_grid = np.zeros((len(rz_grid), len(z_vals)))
        
        for j, z in enumerate(z_vals):
            for i, rz in enumerate(rz_grid):
                # Using linear growth assumption for interpolation grid
                s8_grid[i, j] = self.ksau_core.predict_s8_z(z, rz, 0.0, use_nl=True)
        
        self.s8_interp = RegularGridInterpolator(
            (np.log(rz_grid), z_vals),
            s8_grid,
            method="linear",
            bounds_error=False,
            fill_value=None 
        )

    # --- S8 Resonance Model Methods ---

    def gamma_k(self, k):
        """Gaussian-log-k Resonance Model for gamma(k)"""
        k_gr = 0.001  # Fixed small scale for GR return (from v27.0)
        gr_return = k / (k + k_gr)
        return (self.g_peak * np.exp(-(np.log(k / self.k_res))**2 / (2 * self.sigma**2)) + self.g_asym) * gr_return

    def get_rz(self, k, z):
        """Compute the resonance scale R_z(k, z)"""
        g = self.gamma_k(k)
        r0 = self.r_base_3 * self.alpha_opt * k**(-g)
        return r0 * (1.0 + z)**(-self.beta_ssot)

    def predict_s8(self, k, z):
        """Predict S8 at redshift z for scale k"""
        rz = self.get_rz(k, z)
        # Use log(rz) for interpolation, allow extrapolation as in v27.0
        s8_z = self.s8_interp([[np.log(max(rz, 1e-5)), z]])[0]
        return float(s8_z)

    def predict_s8_z0(self, k, z):
        """Predict effective S8(z=0) observed at redshift z"""
        s8_z = self.predict_s8(k, z)
        a = 1.0 / (1.0 + z)
        return s8_z / (a**self.growth_index)

    # --- H0 Relaxation Model Methods ---

    def h_lcdm(self, z):
        """Background LCDM Hubble rate based on Planck H0"""
        return self.h0_planck * np.sqrt(self.omega_m * (1+z)**3 + self.omega_l)

    def epsilon(self, z):
        """Manifold relaxation factor epsilon(z)"""
        return self.epsilon0 * (1+z)**-3

    def predict_h(self, z):
        """Predict apparent Hubble rate H_app(z) due to geometric relaxation"""
        eps = self.epsilon(z)
        return self.h_lcdm(z) * (1.0 + 3.0 * eps / (1.0 + eps))

    def get_summary(self):
        return {
            "S8_Parameters": {
                "Alpha": self.alpha_opt,
                "Gamma_Peak": self.g_peak,
                "Sigma": self.sigma,
                "Gamma_Asym": self.g_asym,
                "k_res": self.k_res,
                "Beta_SSoT": self.beta_ssot
            },
            "H0_Parameters": {
                "H0_Planck": self.h0_planck,
                "Epsilon0": self.epsilon0,
                "H0_KSAU_z0": self.predict_h(0)
            }
        }

def main():
    parser = argparse.ArgumentParser(description="KSAU Standard Cosmology Engine (SKC)")
    parser.add_argument("--z", type=str, default="0.0", help="Redshift z (comma-separated for multiple)")
    parser.add_argument("--k", type=str, default="0.1", help="Scale k [h/Mpc] (comma-separated for multiple)")
    parser.add_argument("--mode", choices=["s8", "h", "both"], default="both")
    args = parser.parse_args()

    engine = KSAUStandardCosmology()
    
    print("=== KSAU Standard Cosmology Engine (SKC) ===")
    summary = engine.get_summary()
    print(f"S8 Resonance: Alpha={summary['S8_Parameters']['Alpha']:.4f}, k_res={summary['S8_Parameters']['k_res']:.6f}")
    print(f"H0 Relaxation: H0_Planck={summary['H0_Parameters']['H0_Planck']}, H0_KSAU(z=0)={summary['H0_Parameters']['H0_KSAU_z0']:.2f}")
    print("-" * 60)

    z_list = [float(x.strip()) for x in args.z.split(",")]
    k_list = [float(x.strip()) for x in args.k.split(",")]

    if args.mode in ["h", "both"]:
        print(f"{'Redshift z':<12} | {'H_app(z)':<12} | {'H_LCDM(z)':<12} | {'Gap':<12}")
        print("-" * 60)
        for z in z_list:
            h_z = engine.predict_h(z)
            h_lcdm = engine.h_lcdm(z)
            print(f"{z:<12.3f} | {h_z:<12.2f} | {h_lcdm:<12.2f} | {h_z - h_lcdm:<12.2f}")
        print("-" * 60)

    if args.mode in ["s8", "both"]:
        print(f"{'z':<8} | {'k':<8} | {'Rz':<8} | {'S8(z)':<10} | {'S8(z=0)eff':<10}")
        print("-" * 60)
        for z in z_list:
            for k in k_list:
                rz = engine.get_rz(k, z)
                s8_z = engine.predict_s8(k, z)
                s8_z0 = engine.predict_s8_z0(k, z)
                print(f"{z:<8.2f} | {k:<8.2f} | {rz:<8.2f} | {s8_z:<10.4f} | {s8_z0:<10.4f}")
        print("-" * 60)

if __name__ == "__main__":
    main()
