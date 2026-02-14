import numpy as np
import json

def load_data():
    with open("v6.0/data/physical_constants.json", "r") as f:
        constants = json.load(f)
    with open("v6.0/data/topology_assignments.json", "r") as f:
        topologies = json.load(f)
    return constants, topologies

def explore():
    constants, topologies = load_data()
    kappa = constants['kappa']
    C_univ = -0.7087 # Electron base
    
    print(f"{'Particle':<12} | {'N':<2} | {'V':<8} | {'ln(m)_obs':<10} | {'Req. Shift S':<12} | {'S/kappa'}")
    print("-" * 75)
    
    def analyze_sector(sector_key, particles, N_val):
        for p in particles:
            v = topologies[p]['volume']
            lnm_obs = np.log(constants[sector_key][p]['observed_mass'])
            
            # Formula: lnm_obs = N * kappa * V + C_univ - S
            # => S = N * kappa * V + C_univ - lnm_obs
            S = N_val * kappa * v + C_univ - lnm_obs
            s_over_kappa = S / kappa
            
            print(f"{p:<12} | {N_val:<2} | {v:<8.4f} | {lnm_obs:<10.4f} | {S:<12.4f} | {s_over_kappa:.2f}")

    print("LEPTONS (N=20)")
    analyze_sector('leptons', ["Electron", "Muon", "Tau"], 20)
    
    print("\nQUARKS (N=10)")
    analyze_sector('quarks', ["Up", "Down", "Strange", "Charm", "Bottom", "Top"], 10)

if __name__ == "__main__":
    explore()
