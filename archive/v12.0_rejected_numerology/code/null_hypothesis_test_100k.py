import numpy as np
import json
from pathlib import Path
import random

def load_ssot():
    data_path = Path("v6.0/data/physical_constants.json")
    with open(data_path, "r") as f:
        return json.load(f)

def run_expanded_mc_test():
    phys = load_ssot()
    m_e = phys['leptons']['Electron']['observed_mass'] * 1e6 # eV
    m_planck = phys['gravity']['m_planck_gev'] * 1e9 # eV
    X_obs = np.log(m_planck / m_e)
    
    print(f"Target X_obs: {X_obs:.8f}")
    
    N_trials = 100000
    hits = 0
    # Search range expanded to q=200
    q_max = 200
    threshold = 0.00011 # 0.011% precision
    
    print(f"Running 100,000 Monte Carlo trials (q_max={q_max}) for hierarchy coincidence...")
    
    for _ in range(N_trials):
        q = random.randint(1, q_max)
        p = random.randint(15 * q, 18 * q)
        X_pred = np.pi * (p / q)
        error = abs(X_pred / X_obs - 1)
        if error < threshold:
            hits += 1
            
    p_value = hits / N_trials
    print(f"Hits within {threshold*100:.3f}%: {hits}")
    print(f"Estimated p-value: {p_value:.6f}")
    
    if p_value < 0.001:
        print("Verdict: Statistical significance maintained even with expanded search.")

if __name__ == "__main__":
    run_expanded_mc_test()
