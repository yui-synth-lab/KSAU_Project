#!/usr/bin/env python3
"""
KSAU v27.0 Session 3 — H0 Tension & Geometric Relaxation
=====================================================
Investigates the possibility that the manifold diameter R_cell 
evolves with redshift z, leading to an apparent H0 tension.

Theory:
R_cell(z) = R_cell_geom * (1 + epsilon(z))
epsilon(z) = (alpha * beta) * (1 + z)^-3
where alpha = 1/48, beta = 13/6 (KSAU fundamental constants).
This corresponds to a "relaxation" of the manifold as energy density drops.

Effective Expansion Rate:
H_app(z) = H_LCDM(z) * (1 + 3 * epsilon(z) / (1 + epsilon(z)))
"""

import sys
import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Path setup
BASE = Path("E:/Obsidian/KSAU_Project")
COSMO_CONFIG = BASE / "v6.0" / "data" / "cosmological_constants.json"

def main():
    # 1. Load Constants
    with open(COSMO_CONFIG, "r", encoding="utf-8") as f:
        cosmo = json.load(f)
    
    h0_planck = cosmo["H0_planck"] # 67.4
    h0_local = cosmo["H0_local"]   # 73.0
    omega_m = cosmo["omega_m0"]    # 0.315
    omega_l = cosmo["omega_lambda0"] # 0.685
    
    alpha = cosmo["alpha_ksau"]
    beta = cosmo["beta_ksau"]
    epsilon0 = alpha * beta # ~0.0451
    
    print(f"KSAU Geometric Constants:")
    print(f"  alpha: {alpha:.6f}")
    print(f"  beta : {beta:.6f}")
    print(f"  epsilon0 (z=0): {epsilon0:.6f}")
    print("-" * 40)

    # 2. Define Model
    def h_lcdm(z):
        return h0_planck * np.sqrt(omega_m * (1+z)**3 + omega_l)

    def epsilon(z):
        return epsilon0 * (1+z)**-3

    def h_app(z):
        eps = epsilon(z)
        # The factor 3 comes from the derivative of (1+z)^-3
        return h_lcdm(z) * (1.0 + 3.0 * eps / (1.0 + eps))

    # 3. Analyze at key redshifts
    z_vals = np.linspace(0, 2.0, 100)
    h_app_vals = [h_app(z) for z in z_vals]
    h_lcdm_vals = [h_lcdm(z) for z in z_vals]

    print(f"H(z) Predictions:")
    print(f"  z=0.00: H_LCDM = {h_lcdm(0):.2f} | H_app = {h_app(0):.2f} (Gap: {h_app(0)-h_lcdm(0):.2f})")
    print(f"  z=0.10: H_LCDM = {h_lcdm(0.1):.2f} | H_app = {h_app(0.1):.2f}")
    print(f"  z=0.50: H_LCDM = {h_lcdm(0.5):.2f} | H_app = {h_app(0.5):.2f}")
    print(f"  z=1.00: H_LCDM = {h_lcdm(1.0):.2f} | H_app = {h_app(1.0):.2f}")
    print(f"  z=2.00: H_LCDM = {h_lcdm(2.0):.2f} | H_app = {h_app(2.0):.2f}")
    
    # 4. Compare with Benchmarks
    h0_app_z0 = h_app(0)
    print("-" * 40)
    print(f"Benchmark Comparison:")
    print(f"  Planck H0 (CMB): {h0_planck}")
    print(f"  SH0ES H0 (Local): {h0_local}")
    print(f"  KSAU H_app(0)  : {h0_app_z0:.2f}")
    
    # Note: SH0ES measures an effective H0 by fitting low-z SNe. 
    # Let's average H_app(z) / E_lcdm(z) over z in [0.02, 0.15]
    z_local = np.linspace(0.02, 0.15, 20)
    h_extrapolated = np.mean([h_app(z) / (h_lcdm(z)/h0_planck) for z in z_local])
    print(f"  SH0ES-like Extrapolated H0 (z in [0.02, 0.15]): {h_extrapolated:.2f}")

    # 4.5 Chi-square Evaluation
    # SH0ES typical uncertainty is ~1.0 km/s/Mpc
    h0_sh0es_err = 1.0
    chi2_sh0es = ((h_extrapolated - h0_local)**2) / (h0_sh0es_err**2)
    print(f"  Chi-square (vs SH0ES): {chi2_sh0es:.2f} ({(chi2_sh0es)**0.5:.2f} sigma)")

    # 5. Save Results
    results = {
        "model": "R_cell(z) = R_cell_geom * (1 + epsilon0 * (1+z)^-3)",
        "epsilon0": float(epsilon0),
        "h0_planck": float(h0_planck),
        "h0_ksau_z0": float(h0_app_z0),
        "h0_sh0es_equivalent": float(h_extrapolated),
        "chi2_sh0es": float(chi2_sh0es),
        "consistency": {
            "sh0es_match": bool(chi2_sh0es < 4.0), # 2 sigma threshold
            "ksau_sso_match": bool(abs(h0_app_z0 - cosmo.get("H0_ksau", 76.05)) < 0.5)
        }
    }
    
    out_path = BASE / "v27.0" / "data" / "h0_evolution_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    # 6. Visualization
    plt.figure(figsize=(10, 6))
    plt.plot(z_vals, h_app_vals, label="KSAU Apparent H(z) (Geometric Relaxation)", color="red", lw=2)
    plt.plot(z_vals, h_lcdm_vals, label="LCDM Background H(z) (Planck)", color="blue", linestyle="--")
    plt.axhline(h0_local, color="green", linestyle=":", label="SH0ES (Local)")
    plt.axhline(h0_planck, color="blue", linestyle=":", label="Planck (CMB)")
    plt.xlabel("Redshift z")
    plt.ylabel("H(z) [km/s/Mpc]")
    plt.title("H0 Tension Resolution via Manifold Relaxation")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.savefig(BASE / "v27.0" / "figures" / "h0_evolution_ksau.png")
    print(f"Figures saved to v27.0/figures/h0_evolution_ksau.png")

if __name__ == "__main__":
    main()
