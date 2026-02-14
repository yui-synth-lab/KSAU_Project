import numpy as np
import json

def load_data():
    with open("v6.0/data/physical_constants.json", "r") as f:
        constants = json.load(f)
    with open("v6.0/data/topology_assignments.json", "r") as f:
        topologies = json.load(f)
    return constants, topologies

def test_shift_theory():
    constants, topologies = load_data()
    kappa = constants['kappa']
    
    # Universal constant
    C_univ = -0.7087 # Electron ln(m)
    
    # Sector N values
    N_lepton = 20
    N_quark = 10
    
    # Discrete Shifts
    SHIFT_QUARK = 60 * kappa # A5 symmetry barrier
    SHIFT_BOTTOM = 24 * kappa # Niemeier rank / Pi deficit
    
    print(f"{'Particle':<12} | {'ln(m)_obs':<10} | {'ln(m)_pred':<10} | {'Error'}")
    print("-" * 50)
    
    # Test Leptons
    for p in ["Electron", "Muon", "Tau"]:
        v = topologies[p]['volume']
        lnm_obs = np.log(constants['leptons'][p]['observed_mass'])
        lnm_pred = N_lepton * kappa * v + C_univ
        print(f"{p:<12} | {lnm_obs:<10.4f} | {lnm_pred:<10.4f} | {lnm_pred - lnm_obs:.4f}")

    print("-" * 50)
    # Test Quarks
    for p in ["Up", "Down", "Strange", "Charm", "Bottom", "Top"]:
        v = topologies[p]['volume']
        lnm_obs = np.log(constants['quarks'][p]['observed_mass'])
        
        # Base prediction with Quark Shift
        lnm_pred = N_quark * kappa * v + C_univ - SHIFT_QUARK
        
        # Special case for Bottom (Niemeier deficit)
        if p == "Bottom":
            lnm_pred -= SHIFT_BOTTOM
            
        print(f"{p:<12} | {lnm_obs:<10.4f} | {lnm_pred:<10.4f} | {lnm_pred - lnm_obs:.4f}")

if __name__ == "__main__":
    test_shift_theory()
