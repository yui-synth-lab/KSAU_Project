#!/usr/bin/env python3
"""
KSAU v30.0 - Alpha False Positive Test (Session 6)
==================================================
Monte Carlo validation of the geometric alpha discovery.
Estimates the probability of finding a match within 0.34% error 
given the search space complexity.

Search Space:
- Form: C * b1^p1 * b2^p2
- Coeffs (11): [1, 2, 3, 4, 1/2, 1/3, 1/4, 2/3, 3/2, 3/4, 4/3]
- Powers (8): [-3, -2, -1, -0.5, 0.5, 1, 2, 3]
- Bases (5): [kappa, pi, e, 24, N_leech]

Target: alpha_em = 0.00729735
Tolerance: 0.34%
"""

import numpy as np
import json
from pathlib import Path
from itertools import product

def run_significance_test():
    print("=== Alpha Derivation Significance Test ===")
    
    # Load Constants
    base_path = Path(__file__).resolve().parent.parent.parent
    with open(base_path / "v6.0/data/physical_constants.json", "r") as f:
        phys = json.load(f)
    
    # Constants
    alpha_target = phys['alpha_em']
    kappa = phys['kappa']
    pi = phys['pi']
    e = np.e
    D = 24
    N = 196560
    
    bases = [kappa, pi, e, D, N]
    coeffs = [1, 2, 3, 4, 0.5, 0.333333, 0.25, 0.666667, 1.5, 0.75, 1.333333]
    powers = [-3, -2, -1, -0.5, 0.5, 1, 2, 3]
    
    print(f"Target Alpha: {alpha_target}")
    print(f"Match Tolerance: 0.34%")
    
    # 1. Count total candidates
    # Form 1: C * b1^p1
    count_1 = len(coeffs) * len(bases) * len(powers)
    
    # Form 2: C * b1^p1 * b2^p2
    # Note: b1 and b2 are from same list. Order doesn't matter for multiplication 
    # but (b1, p1) (b2, p2) pairs matter.
    # Total unique combinations of (b^p) terms?
    term_opts = len(bases) * len(powers) # 5 * 8 = 40 terms
    # We select 2 terms with replacement: 40 * 40 = 1600.
    # Multiplied by 11 coeffs: 17600.
    count_2 = len(coeffs) * (len(bases) * len(powers))**2
    
    total_candidates = count_1 + count_2
    print(f"Total Formula Candidates: {total_candidates}")
    
    # 2. Generate all values
    values = []
    
    # Single term
    for c in coeffs:
        for b in bases:
            for p in powers:
                values.append(c * (b**p))
                
    # Double term
    # Optimization: precompute terms
    terms = []
    for b in bases:
        for p in powers:
            terms.append(b**p)
            
    for c in coeffs:
        for t1 in terms:
            for t2 in terms:
                values.append(c * t1 * t2)
                
    values = np.array(values)
    
    # Filter physical range?
    # We only care about values "close" to alpha?
    # No, we assume the universe doesn't care.
    # But usually we check "order of magnitude".
    # Let's count matches within 0.34% of target.
    
    error = np.abs(values - alpha_target) / alpha_target
    matches = np.sum(error < 0.0034)
    
    print(f"Matches found within 0.34%: {matches}")
    match_rate = matches / total_candidates
    print(f"Probability of chance match (match_rate): {match_rate:.6f}")
    
    # 3. Control Test (Random Targets)
    # Pick random numbers in the range [0.001, 0.01] (order of magnitude of alpha)
    # and see how often we hit them.
    print("\n--- Control Test (Random Targets in [0.001, 0.01]) ---")
    n_controls = 1000
    random_targets = np.random.uniform(0.001, 0.01, n_controls)
    hits = 0
    for t in random_targets:
        err = np.abs(values - t) / t
        if np.min(err) < 0.0034:
            hits += 1
            
    fpr = hits / n_controls
    print(f"False Positive Rate (Random Targets): {fpr:.2%}")
    
    if fpr > 0.05:
        print("CONCLUSION: FAILED. The formula space is too dense.")
        print("The 'discovery' is statistically indistinguishable from numerology.")
    else:
        print("CONCLUSION: PASSED. The formula space is sparse in this region.")

if __name__ == "__main__":
    run_significance_test()
