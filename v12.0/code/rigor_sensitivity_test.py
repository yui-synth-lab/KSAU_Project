import numpy as np
import json
from pathlib import Path

def load_ssot():
    data_path = Path("v6.0/data/physical_constants.json")
    with open(data_path, "r") as f:
        return json.load(f)

def run_sensitivity_analysis():
    phys = load_ssot()
    m_e = phys['leptons']['Electron']['observed_mass'] # MeV
    m_planck_raw = phys['gravity']['m_planck_gev'] 
    
    # 1. Planck Mass Definitions
    m_planck_non_red = m_planck_raw * 1e3 # MeV
    m_planck_red = m_planck_non_red / np.sqrt(8 * np.pi)
    
    X_obs_non_red = np.log(m_planck_non_red / m_e)
    X_obs_red = np.log(m_planck_red / m_e)
    
    print("--- 1. Planck Mass Sensitivity Analysis ---")
    print(f"Non-reduced X_obs: {X_obs_non_red:.6f}")
    print(f"Reduced X_obs:     {X_obs_red:.6f}")
    
    X_theory = 16.4 * np.pi
    err_non_red = (X_theory / X_obs_non_red - 1) * 100
    err_red = (X_theory / X_obs_red - 1) * 100
    
    print(f"\nTheory X (16.4*pi): {X_theory:.6f}")
    print(f"Error (Non-reduced): {err_non_red:+.6f}%")
    print(f"Error (Reduced):     {err_red:+.6f}%")

    # 2. Alternative Level Exclusion Test
    print("\n--- 2. Alternative Level (N) Exclusion Test ---")
    print(f"{'Level N':<10} | {'Genus':<8} | {'X_pred':<15} | {'Error (%)'}")
    print("-" * 60)
    
    test_levels = [31, 37, 41, 43, 47, 53]
    genera = {31:2, 37:2, 41:3, 43:3, 47:3, 53:4}
    
    for N in test_levels:
        # Test N-based prediction: X = pi * (16 + 24/N)
        X_pred = np.pi * (16 + 24/N)
        error = (X_pred / X_obs_non_red - 1) * 100
        print(f"{N:<10} | {genera[N]:<8} | {X_pred:<15.6f} | {error:+.4f}%")

if __name__ == "__main__":
    run_sensitivity_analysis()
