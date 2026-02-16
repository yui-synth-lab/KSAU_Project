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
    
    m_planck_non_red = m_planck_raw * 1e3 # MeV
    X_obs = np.log(m_planck_non_red / m_e)
    
    print("--- 1. Planck Mass Sensitivity Analysis ---")
    print(f"Non-reduced X_obs: {X_obs:.6f}")
    
    X_theory = 16.4 * np.pi
    err_non_red = (X_theory / X_obs - 1) * 100
    print(f"Theory X (16.4*pi): {X_theory:.6f}")
    print(f"Error (Non-reduced): {err_non_red:+.6f}%")

    # 2. Symmetry Group Order Test (Fix based on Claude's Bug Report)
    print("\n--- 2. Symmetry Group Order Test (X = 16pi + 24pi/k) ---")
    print(f"{'Group |G|':<20} | {'X_pred':<15} | {'Error (%)'}")
    print("-" * 60)
    
    # Testing whether |A5|=60 is uniquely selected as the symmetry divisor
    symmetry_orders = [
        (24, "24 (Niemeier rank)"),
        (48, "48 (Double cover)"),
        (60, "60 (A5 Icosahedral)"),
        (120, "120 (A5 x Z2)"),
        (168, "168 (PSL(2,7))")
    ]
    
    for k, label in symmetry_orders:
        X_pred = np.pi * (16 + 24/k)
        error = (X_pred / X_obs - 1) * 100
        print(f"{label:<20} | {X_pred:<15.6f} | {error:+.4f}%")

    # 3. Modular Level Test (X = 2*N*pi/5)
    print("\n--- 3. Modular Level Test (X = 2*N*pi/5) ---")
    print(f"{'Level N':<10} | {'X_pred':<15} | {'Error (%)'}")
    print("-" * 40)
    
    # Testing whether N=41 uniquely yields 16.4*pi
    test_levels = [37, 41, 43, 47]
    for N in test_levels:
        X_pred = 2 * N * np.pi / 5
        error = (X_pred / X_obs - 1) * 100
        print(f"N={N:<8} | {X_pred:<15.6f} | {error:+.4f}%")

if __name__ == "__main__":
    run_sensitivity_analysis()
