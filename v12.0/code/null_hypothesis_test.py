import json
from pathlib import Path
import numpy as np

def load_ssot():
    data_path = Path("v6.0/data/physical_constants.json")
    with open(data_path, "r") as f:
        return json.load(f)

def run_null_hypothesis_test():
    phys = load_ssot()
    m_e_target = phys['leptons']['Electron']['observed_mass'] * 1e6 # eV
    # SSoT Planck mass (non-reduced)
    m_planck = phys['gravity']['m_planck_gev'] * 1e9 # eV
    
    X_target = np.log(m_planck / m_e_target)
    ratio_target = X_target / np.pi
    
    print(f"Target Ratio (X/pi): {ratio_target:.6f}")
    
    N = 10000
    hits = 0
    
    print(f"Running Monte Carlo Null Hypothesis (N={N})...")
    
    results = []
    for _ in range(N):
        import random
        q = random.randint(1, 100)
        p = random.randint(10 * q, 20 * q)
        ratio = p / q
        
        m_pred = m_planck * np.exp(-ratio * np.pi)
        error = abs(m_pred / m_e_target - 1)
        
        if error < 0.006:
            hits += 1
            results.append((p, q, ratio, error))
            
    p_value = hits / N
    print(f"Hits within 0.6% error: {hits}")
    print(f"Estimated p-value: {p_value:.4f}")
    
    if p_value > 0.05:
        print("\nCONCLUSION: HIGH PROBABILITY OF COINCIDENCE.")
    else:
        print("\nCONCLUSION: POTENTIALLY INTERESTING.")

if __name__ == "__main__":
    run_null_hypothesis_test()
