import numpy as np
import json
from pathlib import Path

def load_ssot_data():
    # Load physical constants from SSoT (v6.0)
    data_path = Path("v6.0/data/physical_constants.json")
    with open(data_path, "r") as f:
        return json.load(f)

def calculate_leech_vacuum_entropy():
    """
    Calculates the static information entropy of the Leech Lattice 
    projected into 4-dimensional spacetime.
    """
    phys = load_ssot_data()
    m_e = phys['leptons']['Electron']['observed_mass']
    # Load Planck mass from SSoT
    m_planck = phys['gravity']['m_planck_gev'] * 1e3 # MeV
    
    # Coordination number of the Leech Lattice (Kissing Number)
    K_leech = 196560
    S_unit = np.log(K_leech)
    
    # Hierarchy factor X = ln(M_pl / m_e)
    X_target = np.log(m_planck / m_e)
    
    print(f"Leech Connectivity K = {K_leech}")
    print(f"Information Density per Dimension S = {S_unit:.6f}")
    print(f"Target Hierarchy Factor X (from SSoT) = {X_target:.6f}")
    
    # 4D Entropy component
    entropy_4d = 4 * S_unit
    print(f"4D Projected Entropy (4*S) = {entropy_4d:.6f}")
    
    kappa = phys.get('kappa', np.pi/24)
    residual = X_target - entropy_4d
    print(f"Residual (X - 4*S) = {residual:.6f}")
    print(f"Residual in units of kappa: {residual/kappa:.4f}")
    
    print("\n--- Geometric Foundation ---")
    print("The electron mass scale is fundamentally constrained by the connectivity")
    print("of the 24-dimensional Leech lattice vacuum across 4-dimensional spacetime.")
    print(f"Core term 4*ln(K) accounts for {entropy_4d/X_target*100:.2f}% of the hierarchy.")

if __name__ == "__main__":
    calculate_leech_vacuum_entropy()
