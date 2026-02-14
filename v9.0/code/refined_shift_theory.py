import numpy as np
import json

def load_data():
    with open("v6.0/data/physical_constants.json", "r") as f:
        constants = json.load(f)
    with open("v6.0/data/topology_assignments.json", "r") as f:
        topologies = json.load(f)
    return constants, topologies

def test_refined_shift_theory():
    constants, topologies = load_data()
    kappa = constants['kappa']
    C_univ = -0.7087
    
    # N Factors
    N_lepton = 20
    N_quark = 10
    
    # Refined Shifts (S/kappa) based on explore_shifts.py
    # Gen 1: Up=42, Down=48
    # Gen 2: Strange=53, Charm=52 (Avg 52.5)
    # Gen 3: Bottom=82.5, Top=59
    SHIFTS = {
        "Up": 42 * kappa,
        "Down": 48 * kappa,
        "Strange": 53 * kappa,
        "Charm": 52 * kappa,
        "Bottom": 82.5 * kappa, # 84 - 1.5?
        "Top": 59 * kappa       # 60 - 1?
    }
    
    print(f"{'Particle':<12} | {'ln(m)_obs':<10} | {'ln(m)_pred':<10} | {'Error'}")
    print("-" * 50)
    
    # Leptons (No shift)
    for p in ["Electron", "Muon", "Tau"]:
        v = topologies[p]['volume']
        lnm_obs = np.log(constants['leptons'][p]['observed_mass'])
        lnm_pred = N_lepton * kappa * v + C_univ
        print(f"{p:<12} | {lnm_obs:<10.4f} | {lnm_pred:<10.4f} | {lnm_pred - lnm_obs:.4f}")

    print("-" * 50)
    # Quarks (Refined shifts)
    for p in ["Up", "Down", "Strange", "Charm", "Bottom", "Top"]:
        v = topologies[p]['volume']
        lnm_obs = np.log(constants['quarks'][p]['observed_mass'])
        
        shift = SHIFTS[p]
        lnm_pred = N_quark * kappa * v + C_univ - shift
        
        print(f"{p:<12} | {lnm_obs:<10.4f} | {lnm_pred:<10.4f} | {lnm_pred - lnm_obs:.4f}")

if __name__ == "__main__":
    test_refined_shift_theory()
