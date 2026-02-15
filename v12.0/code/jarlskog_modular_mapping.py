import numpy as np
import json
from pathlib import Path

def load_ssot():
    data_path = Path("v6.0/data/physical_constants.json")
    with open(data_path, "r") as f:
        return json.load(f)

def analyze_jarlskog_modular_mapping():
    phys = load_ssot()
    kappa = phys.get('kappa', np.pi/24)
    J_obs = phys['cp_violation']['jarlskog_J']
    
    print(f"Observed Jarlskog J = {J_obs:.2e}")
    
    ln_J = np.log(J_obs)
    n_kappa = ln_J / kappa
    
    print(f"ln(J) = {ln_J:.4f}")
    print(f"ln(J) / kappa = {n_kappa:.4f}")
    
    N = 41
    candidates = [
        ("exp(-2*N*kappa)", np.exp(-2 * N * kappa)),
        ("exp(-2*(N-1)*kappa)", np.exp(-2 * (N-1) * kappa)),
        ("exp(-2*(N+1)*kappa)", np.exp(-2 * (N+1) * kappa))
    ]
    
    print("\n--- Modular Candidate Mapping ---")
    for label, val in candidates:
        error = (val / J_obs - 1) * 100
        print(f"{label:<25} | Value: {val:.2e} | Error: {error:+.2f}%")

if __name__ == "__main__":
    analyze_jarlskog_modular_mapping()
