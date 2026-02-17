"""
KSAU v16.1 Supplementary Material: Monte Carlo Null Hypothesis Test
Goal: Prove that the accuracy of the Unified Density Formula 
      is statistically significant (p < 0.001).
"""

import numpy as np

def run_monte_carlo_test(iterations=100000):
    # Target Observed Density
    rho_obs = 1.530e-5
    
    # Ranges based on geometric invariants (K-numbers, mu, volumes)
    # mu: [1, 500] -> Covers low-genus modular curves X_0(N) where most physics resides.
    # K: [1, 200000] -> Upper bound set by K_24 = 196560 (Leech Lattice maximum).
    # V_ratio: [1e-10, 1e-5] -> Reflected by the scale separation between 24D and 4D volumes.
    # K_ratio: [1e-5, 1e-1] -> Heuristic range for cross-dimensional packing efficiency.
    # r_locking: [0.01, 1.0] -> Efficiency factor for 3D boundary locking.
    
    success_count = 0
    results = []
    
    print(f"Running {iterations} iterations of Random Geometric Combinations...")
    
    for _ in range(iterations):
        # Randomly sample values from the "Geometric Search Space"
        r_mu = np.random.uniform(1, 500)
        r_K_lost = np.random.uniform(1, 200000)
        r_vol_ratio = np.random.uniform(1e-10, 1e-5)
        r_K_ratio = np.random.uniform(1e-5, 1e-1)
        r_locking = np.random.uniform(0.01, 1.0)
        
        r_rho = (r_K_lost / r_mu) * (r_vol_ratio * r_K_ratio) * r_locking
        
        # Check if random result is within 3% of observed (similar to our 97.35%)
        if abs(r_rho - rho_obs) / rho_obs < 0.03:
            success_count += 1
            
    p_value = success_count / iterations
    
    print("="*80)
    print(f"{'KSAU v16.1: Statistical Significance Report':^80}")
    print("="*80)
    print(f"Null Hypothesis: Random combinations of geometric invariants can match rho_obs.")
    print(f"Iterations      : {iterations}")
    print(f"Matches (<3%)   : {success_count}")
    print(f"P-Value         : {p_value:.6f}")
    print("-" * 80)
    
    if p_value < 0.001:
        print("RESULT: STATISTICALLY SIGNIFICANT (p < 0.001)")
        print("✓ The alignment in v16.1 is unlikely to be a numerical accident.")
    else:
        print("RESULT: WEAK ALIGNMENT")
    print("="*80)

if __name__ == "__main__":
    run_monte_carlo_test()
