"""
KSAU v16.1 Supplementary Material: Monte Carlo Sensitivity Analysis
Goal: Analyze how expanding the geometric search space affects the p-value.
      This ensures the result is robust and not a result of "p-hacking" 
      via narrow range selection.
"""

import numpy as np

def sample_and_test(iterations, ranges, rho_obs):
    success_count = 0
    for _ in range(iterations):
        r_mu = np.random.uniform(ranges['mu'][0], ranges['mu'][1])
        r_K_lost = np.random.uniform(ranges['K'][0], ranges['K'][1])
        r_vol_ratio = np.random.uniform(ranges['vol'][0], ranges['vol'][1])
        r_K_ratio = np.random.uniform(ranges['K_rat'][0], ranges['K_rat'][1])
        r_locking = np.random.uniform(ranges['lock'][0], ranges['lock'][1])
        
        r_rho = (r_K_lost / r_mu) * (r_vol_ratio * r_K_ratio) * r_locking
        if abs(r_rho - rho_obs) / rho_obs < 0.03:
            success_count += 1
    return success_count / iterations

def run_sensitivity_analysis():
    rho_obs = 1.530e-5
    iterations = 50000
    
    # Base ranges (v16.1 standard)
    base_ranges = {
        'mu': [1, 500],
        'K': [1, 200000],
        'vol': [1e-10, 1e-5],
        'K_rat': [1e-5, 1e-1],
        'lock': [0.01, 1.0]
    }
    
    multipliers = [1, 2, 5, 10]
    
    print(f"{'Search Space Multiplier':<25} | {'P-Value':<10}")
    print("-" * 40)
    
    for m in multipliers:
        # Expand ranges by the multiplier m
        # mu and K upper bounds increased, Vol ratio lower bound decreased
        test_ranges = {
            'mu': [1, base_ranges['mu'][1] * m],
            'K': [1, base_ranges['K'][1] * m],
            'vol': [base_ranges['vol'][0] / m, base_ranges['vol'][1] * m],
            'K_rat': [base_ranges['K_rat'][0] / m, base_ranges['K_rat'][1]],
            'lock': [0.01, 1.0]
        }
        
        p_val = sample_and_test(iterations, test_ranges, rho_obs)
        print(f"{m:<25} | {p_val:<10.6f}")

if __name__ == "__main__":
    print("Running Sensitivity Analysis on Monte Carlo Null Hypothesis...")
    run_sensitivity_analysis()
