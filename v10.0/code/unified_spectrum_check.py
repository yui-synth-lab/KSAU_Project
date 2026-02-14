import numpy as np
import json
import matplotlib.pyplot as plt

def load_data():
    with open("v10.0/data/unified_particle_dataset.json", "r") as f:
        data = json.load(f)
    return data

def check_spectrum():
    data = load_data()
    kappa = data['metadata']['universal_constants']['kappa']
    C_univ = data['metadata']['universal_constants']['C_universal']
    
    print(f"{'Particle':<10} | {'Sec':<4} | {'N':<2} | {'V':<8} | {'ln(m)_obs':<10} | {'ln(m)_pred':<10} | {'Error'}")
    print("-" * 75)
    
    sectors = {
        "Lepton": 20,
        "Quark": 10,
        "Boson": 6
    }
    
    results = []
    
    for p in data['particles']:
        name = p['name']
        sector = p['sector']
        v = p['volume']
        lnm_obs = np.log(p['mass_mev'])
        shift = p['shift_kappa'] * kappa
        
        N = sectors[sector]
        
        # Formula: ln(m) = N * kappa * V + C_univ - shift
        lnm_pred = N * kappa * v + C_univ - shift
        
        error = lnm_pred - lnm_obs
        print(f"{name:<10} | {sector[0]:<4} | {N:<2} | {v:<8.4f} | {lnm_obs:<10.4f} | {lnm_pred:<10.4f} | {error:.4f}")
        
        results.append(error**2)
        
    mse = np.mean(results)
    print("-" * 75)
    print(f"Global MSE: {mse:.6f}")
    
    # R2 Calculation
    obs_vals = [np.log(p['mass_mev']) for p in data['particles']]
    mean_obs = np.mean(obs_vals)
    ss_tot = sum((x - mean_obs)**2 for x in obs_vals)
    ss_res = sum(results)
    r2 = 1 - (ss_res / ss_tot)
    print(f"Global R^2: {r2:.6f}")

if __name__ == "__main__":
    check_spectrum()
