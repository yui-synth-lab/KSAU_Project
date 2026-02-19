import numpy as np
import pandas as pd
import json

def calculate_branching(v, e):
    return e / v

def run_monte_carlo_polytopes():
    # Regular 4-polytopes
    polytopes = {
        "5-cell": {"v": 5, "e": 10},
        "8-cell": {"v": 16, "e": 32},
        "16-cell": {"v": 8, "e": 24},
        "24-cell": {"v": 24, "e": 96},
        "120-cell": {"v": 600, "e": 1200},
        "600-cell": {"v": 120, "e": 720}
    }
    
    results = []
    for name, data in polytopes.items():
        b = calculate_branching(data["v"], data["e"])
        results.append({"name": name, "V": data["v"], "E": data["e"], "B": b})
        
    df_poly = pd.DataFrame(results)
    
    # Target value
    B_obs = 3.9375
    alpha = 1/48
    B_target = 4 - 3*alpha
    
    print("Regular 4-Polytopes Branching Numbers (B = E/V):")
    print(df_poly)
    
    # Uniqueness Test
    closest_poly = df_poly.iloc[(df_poly['B'] - B_obs).abs().argsort()[:1]]
    print(f"\nClosest regular 4-polytope to B_obs={B_obs}:")
    print(closest_poly)
    
    # Probability that a random regular 4-polytope has B=4
    # (Out of 6 types)
    prob_poly = 1/6
    print(f"Probability of selecting a polytope with B=4 by chance: {prob_poly:.4f}")

    print(f"\nTarget B (4 - 3*alpha): {B_target}")
    
    # Null Hypothesis: Random Graphs with 24 vertices
    # How many edges E are needed to get B close to 3.94?
    # B = E/24 => E = 24 * B
    E_needed = 24 * B_obs
    print(f"Edges needed for V=24 to get B={B_obs}: {E_needed}")
    
    # Since E must be integer, closest is E=94 or E=95.
    # B(E=94, V=24) = 94/24 = 3.9167
    # B(E=95, V=24) = 95/24 = 3.9583
    # B(E=96, V=24) = 4.0000 (Ideal 24-cell)
    
    # Statistical Significance:
    # If we assume B is a continuous variable derived from a process,
    # what is the probability that B is within 0.01% of 3.9375?
    
    # Monte Carlo simulation of random graphs (Erdos-Renyi)
    # with V=24 and p such that E_avg = 96.
    p = 96 / (24 * 23 / 2) # 96 / 276
    
    n_sims = 100000
    b_sims = []
    for _ in range(n_sims):
        # Number of edges in a random graph follows Binomial(N_max, p)
        e_sim = np.random.binomial(276, p)
        b_sims.append(e_sim / 24)
        
    b_sims = np.array(b_sims)
    # Check for exact matches since E/24 can hit 3.9375 if E is integer?
    # 3.9375 * 24 = 94.5. So no integer E gives exactly 3.9375.
    
    # Let's count how many have B between 3.9 and 4.0
    count_near = np.sum((b_sims >= 3.9) & (b_sims <= 4.0))
    prob_near = count_near / n_sims
    
    print(f"\nProbability of B falling in [3.9, 4.0] in random G(24, p): {prob_near:.4f}")
    
    # Z-score of B_obs relative to random graph with mean E=96
    mean_b = 96 / 24
    std_e = np.sqrt(276 * p * (1-p))
    std_b = std_e / 24
    z_score = (B_obs - mean_b) / std_b
    print(f"Z-score of B_obs relative to B=4.0: {z_score:.4f}")

if __name__ == "__main__":
    run_monte_carlo_polytopes()
