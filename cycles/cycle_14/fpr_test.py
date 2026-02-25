import numpy as np
import pandas as pd
from scipy import stats
import json

def run_fpr():
    # Data from results.json
    n = 9
    ln_st = np.array([1.0986, 1.6094, 2.1972, 2.4849, 2.9957, 3.5835, 4.2485, 4.5643, 4.7005])
    residual = np.array([-0.6714, 4.3945, 7.0684, 0.0720, 0.6835, 3.3179, 5.6787, 6.3541, 10.0149])
    
    obs_slope, obs_intercept, obs_r, obs_p, obs_std_err = stats.linregress(ln_st, residual)
    obs_r2 = obs_r**2
    
    n_trials = 10000
    count = 0
    for _ in range(n_trials):
        shuffled_res = np.random.permutation(residual)
        s, i, r, p, se = stats.linregress(ln_st, shuffled_res)
        if r**2 >= obs_r2:
            count += 1
            
    fpr = count / n_trials
    print(f"Observed R2: {obs_r2:.4f}")
    print(f"Observed p: {obs_p:.4f}")
    print(f"FPR (10k permutations): {fpr:.4f}")

if __name__ == "__main__":
    run_fpr()
