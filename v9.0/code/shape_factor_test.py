import numpy as np
import json
import matplotlib.pyplot as plt

def load_data():
    with open("v6.0/data/physical_constants.json", "r") as f:
        constants = json.load(f)
    
    with open("v6.0/data/topology_assignments.json", "r") as f:
        topologies = json.load(f)
        
    return constants, topologies

def test_shape_factors():
    constants, topologies = load_data()
    kappa = constants['kappa'] # pi/24
    
    # Target masses (ln(m))
    leptons = constants['leptons']
    quarks = constants['quarks']
    
    # N factors: Lepton=20, Quark=10 (Unified Holographic Slope)
    N_factors = {
        "Electron": 20,
        "Muon": 20,
        "Tau": 20,
        "Up": 10,
        "Down": 10,
        "Strange": 10,
        "Charm": 10,
        "Bottom": 10,
        "Top": 10
    }
    
    print(f"{'Particle':<12} | {'N':<4} | {'V':<8} | {'ln(m)_obs':<10} | {'ln(m)_pred':<10} | {'Error'}")
    print("-" * 70)
    
    results = []
    
    # For now, we need to find the best Intercept C for each sector
    # Or maybe C is universal?
    
    # Let's try to fit C for leptons and quarks separately first
    lepton_data = []
    for p, data in leptons.items():
        v = topologies[p]['volume']
        lnm = np.log(data['observed_mass'])
        n = N_factors[p]
        lepton_data.append((n, v, lnm))
        
    # Fit: lnm = N * kappa * V + C  => C = lnm - N * kappa * V
    lepton_Cs = [lnm - n * kappa * v for n, v, lnm in lepton_data]
    C_lepton = np.mean(lepton_Cs)
    
    for p, data in leptons.items():
        v = topologies[p]['volume']
        lnm_obs = np.log(data['observed_mass'])
        n = N_factors[p]
        lnm_pred = n * kappa * v + C_lepton
        error = lnm_pred - lnm_obs
        print(f"{p:<12} | {n:<4} | {v:<8.4f} | {lnm_obs:<10.4f} | {lnm_pred:<10.4f} | {error:.4f}")
        results.append((p, n, v, lnm_obs, lnm_pred))

    print("-" * 70)
    quark_data = []
    for p, data in quarks.items():
        v = topologies[p]['volume']
        lnm = np.log(data['observed_mass'])
        n = N_factors[p]
        quark_data.append((n, v, lnm))
        
    quark_Cs = [lnm - n * kappa * v for n, v, lnm in quark_data]
    C_quark = np.mean(quark_Cs)
    
    for p, data in quarks.items():
        v = topologies[p]['volume']
        lnm_obs = np.log(data['observed_mass'])
        n = N_factors[p]
        lnm_pred = n * kappa * v + C_quark
        error = lnm_pred - lnm_obs
        print(f"{p:<12} | {n:<4} | {v:<8.4f} | {lnm_obs:<10.4f} | {lnm_pred:<10.4f} | {error:.4f}")
        results.append((p, n, v, lnm_obs, lnm_pred))

    print(f"\nFitted Intercepts: Lepton C = {C_lepton:.4f}, Quark C = {C_quark:.4f}")
    
if __name__ == "__main__":
    test_shape_factors()
