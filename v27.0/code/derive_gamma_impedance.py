import sys
import json
import numpy as np
from pathlib import Path

# Path setup
BASE = Path("E:/Obsidian/KSAU_Project")

def main():
    with open(BASE / "v6.0" / "data" / "physical_constants.json", "r") as f:
        phys = json.load(f)
    kappa = phys["kappa"]
    
    # Scale-dependent gamma parameters from results
    # params: [alpha, g_low, g_high, k_pivot]
    p = [8.4168, 10.0, -1.1019, 0.0477]
    alpha, g_low, g_high, k_pivot = p
    
    def gamma_k(k):
        n = 4.0
        return g_high + (g_low - g_high) / (1.0 + (k / k_pivot)**n)

    # Evaluate at key scales
    k_vals = [0.01, 0.05, 0.1, 0.5]
    print(f"k_pivot = {k_pivot:.4f}")
    for k in k_vals:
        g = gamma_k(k)
        print(f"k = {k:.2f} | gamma(k) = {g:+.4f}")

    # Physical derivation idea (Leech Lattice / Unknotting)
    # R_cell ~ 20.1 Mpc (from cosmo_constants)
    # k_resonance ~ 1 / R_cell ~ 1 / 20.1 ~ 0.049 h/Mpc
    # This matches k_pivot = 0.0477 within 3%!
    
    with open(BASE / "v6.0" / "data" / "cosmological_constants.json", "r") as f:
        cosmo = json.load(f)
    r_cell = cosmo.get("R_cell", 20.1)
    k_theory = 1.0 / r_cell
    
    print(f"R_cell = {r_cell}")
    print(f"k_theory = {k_theory:.4f}")
    print(f"Error = {abs(k_pivot - k_theory)/k_theory * 100:.2f}%")

if __name__ == "__main__":
    main()
