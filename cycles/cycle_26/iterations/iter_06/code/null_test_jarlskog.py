
import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd
import re
from scipy.special import spence

# Setup SSOT
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
ssot_path = project_root / "ssot"
sys.path.insert(0, str(ssot_path))    
from ksau_ssot import SSOT

def parse_vector(vec_str):
    if not isinstance(vec_str, str) or pd.isna(vec_str): return None
    clean_str = vec_str.strip('[]{}')
    parts = re.split(r',\s*', clean_str)
    try:
        nums = [int(p) for p in parts]
        return nums[0], nums[1], nums[2:]
    except: return None

def evaluate_jones_at_q(vector, q_val, is_link):
    if vector is None: return 0j
    min_pow, max_pow, coeffs = vector
    val = 0j
    for i, c in enumerate(coeffs):
        p = min_pow + i
        if is_link: val += c * (q_val ** (p / 2.0))
        else: val += c * (q_val ** p)
    return val

def bloch_wigner(z):
    if abs(z) < 1e-15 or abs(z - 1.0) < 1e-15: return 0.0
    li2 = spence(1-z)
    return np.imag(li2) + np.angle(1-z) * np.log(abs(z))

def main():
    ssot = SSOT()
    consts = ssot.constants()
    knots_df, links_df = ssot.knot_data()
    
    target_j = consts['cp_violation']['jarlskog_J']
    kappa = consts['mathematical_constants']['kappa']
    q_val = np.exp(2j * np.pi / 24)
    
    # Pre-evaluate all Jones values for population to speed up MC
    population = []
    for _, row in knots_df.iterrows():
        vec = parse_vector(row['jones_polynomial_vector'])
        if vec:
            population.append(evaluate_jones_at_q(vec, q_val, False))
    for _, row in links_df.iterrows():
        vec = parse_vector(row['jones_polynomial_vector'])
        if vec:
            population.append(evaluate_jones_at_q(vec, q_val, True))
    
    pop_size = len(population)
    print(f"Population Size: {pop_size}")
    
    # Monte Carlo Null Test
    n_trials = 10000
    rng = np.random.default_rng(42)
    hits = 0
    tolerance = 0.012 # 1.2% error threshold
    
    j_values = []
    for _ in range(n_trials):
        idx = rng.choice(pop_size, 4, replace=False)
        u1, u2, d1, d2 = [population[i] for i in idx]
        
        # Avoid division by zero
        denom = (u1 - d2) * (u2 - d1)
        if abs(denom) < 1e-15: continue
        
        z = ((u1 - d1) * (u2 - d2)) / denom
        d_z = bloch_wigner(z)
        j_val = (4.0/3.0) * (kappa ** 5) * d_z
        
        if abs(j_val - target_j) / target_j < tolerance:
            hits += 1
        j_values.append(j_val)
    
    p_value = hits / n_trials
    print(f"P-value: {p_value:.6f}")
    print(f"Hits:    {hits}")

if __name__ == "__main__":
    main()
