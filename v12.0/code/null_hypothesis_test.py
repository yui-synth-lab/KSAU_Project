import numpy as np
import random

def run_null_hypothesis_test():
    # Target value: ln(M_pl / m_e) / pi ~ 16.4018
    m_e_target = 0.510998950e6
    m_planck = 1.220910e28
    X_target = np.log(m_planck / m_e_target)
    ratio_target = X_target / np.pi
    
    print(f"Target Ratio (X/pi): {ratio_target:.6f}")
    
    N = 10000
    hits = 0
    
    print(f"Running Monte Carlo Null Hypothesis (N={N})...")
    
    results = []
    for _ in range(N):
        # Sample p and q such that ratio p/q is in a reasonable range [10, 20]
        q = random.randint(1, 100)
        p = random.randint(10 * q, 20 * q)
        ratio = p / q
        
        m_pred = m_planck * np.exp(-ratio * np.pi)
        error = abs(m_pred / m_e_target - 1)
        
        if error < 0.006: # 0.6% error threshold
            hits += 1
            results.append((p, q, ratio, error))
            
    p_value = hits / N
    print(f"Hits within 0.6% error: {hits}")
    print(f"Estimated p-value: {p_value:.4f}")
    
    if p_value > 0.05:
        print("\nCONCLUSION: HIGH PROBABILITY OF COINCIDENCE.")
        print("The formula is likely Numerology.")
    else:
        print("\nCONCLUSION: POTENTIALLY INTERESTING.")
        
    print("\nSample of 'Lucky' Ratios found:")
    for p, q, r, err in results[:10]:
        print(f"{p}/{q} = {r:.4f} (Error: {err*100:.4f}%)")

if __name__ == "__main__":
    run_null_hypothesis_test()
