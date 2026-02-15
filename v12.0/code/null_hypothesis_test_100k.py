import numpy as np
import json
from pathlib import Path
import random

def load_ssot():
    data_path = Path("v6.0/data/physical_constants.json")
    with open(data_path, "r") as f:
        return json.load(f)

def run_100k_mc_test():
    phys = load_ssot()
    m_e = phys['leptons']['Electron']['observed_mass'] * 1e6 # eV
    m_planck = phys['gravity']['m_planck_gev'] * 1e9 # eV
    X_obs = np.log(m_planck / m_e)
    
    print(f"Target X_obs: {X_obs:.8f}")
    
    N_trials = 100000
    hits = 0
    threshold = 0.00011 # 0.011% relative error observed for 16.4*pi
    
    print(f"Running 100,000 Monte Carlo trials for hierarchy coincidence...")
    
    # We test the probability of finding a ratio pi*(p/q) that matches X_obs within 0.011%
    # Range for p/q is [15, 18] to cover 16.4
    for _ in range(N_trials):
        q = random.randint(1, 100)
        p = random.randint(15 * q, 18 * q)
        X_pred = np.pi * (p / q)
        error = abs(X_pred / X_obs - 1)
        if error < threshold:
            hits += 1
            
    p_value = hits / N_trials
    print(f"Hits within {threshold*100:.3f}%: {hits}")
    print(f"Estimated p-value: {p_value:.6f}")
    
    # Calculate a pseudo-AIC for the N=41 model vs noise
    # RSS = error^2. For N=41, err ~ 1.1e-4.
    # For a random "lucky" hit, err < 1.1e-4.
    # p-value < 0.0001 usually indicates strong significance.

if __name__ == "__main__":
    run_100k_mc_test()
