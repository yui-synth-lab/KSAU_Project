import numpy as np
import json
from pathlib import Path

def load_ssot():
    data_path = Path("v6.0/data/physical_constants.json")
    with open(data_path, "r") as f:
        return json.load(f)

def resolve_1509_puzzle():
    phys = load_ssot()
    m_e = phys['leptons']['Electron']['observed_mass']
    m_planck = phys['gravity']['m_planck_gev'] * 1e3 # MeV
    X_obs = np.log(m_planck / m_e)
    
    # KSAU Fundamental Invariants
    R_v = 24    # Vacuum Rank
    S_60 = 60   # Icosahedral Symmetry (A5)
    g = 3       # Genus / Generations
    P_max = 23  # Max prime factor of |Co_0|
    R_g = 16    # Gauge Rank (E8 x E8)
    
    print("=== KSAU v12.0 Final Puzzle Resolution ===")
    
    # 1. Deconstructing the Denominator 92
    denominator = R_g + R_g + S_60
    print(f"92 = 16 + 16 + 60 -> Result: {denominator}")
    
    # 2. Deconstructing the Numerator 1509
    numerator = (R_v * S_60) + (g * P_max)
    print(f"1509 = (24 * 60) + (3 * 23) -> Result: {numerator}")
    
    # 3. Hierarchy Calculation
    X_theory = np.pi * (numerator / denominator)
    error = (X_theory / X_obs - 1) * 100
    
    print(f"\nX_obs:    {X_obs:.8f}")
    print(f"X_theory: {X_theory:.8f} (pi * 1509 / 92)")
    print(f"Relative Error: {error:+.6f}%")
    
    # 4. Comparison with 82/5 (Leading Order)
    X_lo = 16.4 * np.pi
    lo_error = (X_lo / X_obs - 1) * 100
    print(f"LO Error: {lo_error:+.6f}%")
    print(f"Improvement Factor: {abs(lo_error) / abs(error):.2f}x")

if __name__ == "__main__":
    resolve_1509_puzzle()
