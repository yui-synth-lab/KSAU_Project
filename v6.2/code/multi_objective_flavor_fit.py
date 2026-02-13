"""
KSAU v6.2: Multi-Objective Flavor Fit
Objective: Find topology assignments that satisfy BOTH CKM precision 
           and Gauge Fission consistency (V_top ~ V_W + V_bottom).

This explores the Pareto frontier between mixing and decay geometry.
"""
import pandas as pd
import numpy as np
import json
import sys
import os
from pathlib import Path
from sympy import sympify
from sklearn.metrics import r2_score
import random

# Load project utilities
sys.path.append(os.path.join(os.path.dirname(__file__), '../../v6.1/code'))
import utils_v61

def evaluate_metrics(assignment, ckm_obs, links_df, v_w_target):
    """Evaluate both CKM R^2 and Fission Residual"""
    # 1. CKM R^2
    A, B, beta, gamma, C = -6.3436, 12.3988, -105.0351, 1.1253, 23.2475
    up_types, down_types = ["Up", "Charm", "Top"], ["Down", "Strange", "Bottom"]
    predictions, observations = [], []

    for i, u in enumerate(up_types):
        for j, d in enumerate(down_types):
            u_row = links_df[links_df['name'] == assignment[u]].iloc[0]
            d_row = links_df[links_df['name'] == assignment[d]].iloc[0]
            
            V_u, V_d = float(u_row['volume']), float(d_row['volume'])
            j_u = utils_v61.get_jones_at_root_of_unity(u_row['jones_polynomial'], n=5)
            j_d = utils_v61.get_jones_at_root_of_unity(d_row['jones_polynomial'], n=5)
            lnJ_u, lnJ_d = np.log(max(1e-10, abs(j_u))), np.log(max(1e-10, abs(j_d)))

            dV, dlnJ, V_bar = abs(V_u - V_d), abs(lnJ_u - lnJ_d), (V_u + V_d) / 2.0
            logit_pred = C + A*dV + B*dlnJ + beta/V_bar + gamma*(dV*dlnJ)
            predictions.append(1.0 / (1.0 + np.exp(-logit_pred)))
            observations.append(ckm_obs[i][j])

    try:
        r2 = r2_score(observations, predictions)
    except:
        r2 = -999

    # 2. Fission Residual
    v_top = float(links_df[links_df['name'] == assignment['Top']].iloc[0]['volume'])
    v_bottom = float(links_df[links_df['name'] == assignment['Bottom']].iloc[0]['volume'])
    residual = abs(v_top - (v_w_target + v_bottom))

    return r2, residual

def run_multi_objective_search(n_samples=100000):
    print("="*70)
    print("KSAU v6.2: Multi-Objective Flavor Fit Search")
    print(f"Goal: Maximize CKM R2 & Minimize |V_top - (V_W + V_bot)|")
    print("="*70)

    # Load SSoT
    consts = utils_v61.load_constants()
    _, links_df = utils_v61.load_data()
    ckm_obs = np.array(consts['ckm']['matrix'])
    
    # W Target Volume
    kappa = consts['kappa']
    bq = -(7 + 7 * kappa)
    v_w_target = (np.log(consts['bosons']['W']['observed_mass']) - bq) / (10 * kappa)

    # Generation pools (Search Space)
    gen_constraints = {
        1: {'v_min': 5, 'v_max': 7},
        2: {'v_min': 8, 'v_max': 12},
        3: {'v_min': 12, 'v_max': 17}
    }
    
    pools = {}
    for q_name, q_meta in consts['quarks'].items():
        gen = q_meta['generation']
        comp = 2 if q_name in ['Up', 'Charm', 'Top'] else 3
        c = gen_constraints[gen]
        pools[q_name] = links_df[
            (links_df['components'] == comp) & 
            (links_df['volume'] >= c['v_min']) & (links_df['volume'] <= c['v_max'])
        ].copy()

    best_r2_overall = -999
    best_residual_overall = 999
    pareto_candidates = []

    mass_order = ['Up', 'Down', 'Strange', 'Charm', 'Bottom', 'Top']

    print(f"Sampling {n_samples:,} configurations...")
    for i in range(n_samples):
        if i % 500 == 0:
            print(f"  Progress: {i:,}/{n_samples:,} configurations sampled...")
        
        assignment = {q: pools[q].sample(1).iloc[0]['name'] for q in mass_order}
        
        # Constraints: Mass Hierarchy
        vols = {q: links_df[links_df['name'] == assignment[q]].iloc[0]['volume'] for q in mass_order}
        if [q for q, v in sorted(vols.items(), key=lambda x: x[1])] != mass_order:
            continue
            
        r2, res = evaluate_metrics(assignment, ckm_obs, links_df, v_w_target)
        
        # Track Pareto Front (Simplified: R2 > 0.98 and Minimize Residual)
        if r2 > 0.99 and res < 10.0:
            pareto_candidates.append({'assignment': assignment, 'r2': r2, 'residual': res})
            print(f"  [Found Candidate] R2: {r2:.4f} | Residual: {res:.4f}")

        if r2 > best_r2_overall: best_r2_overall = r2
        if res < best_residual_overall: best_residual_overall = res

    print("\n" + "="*70)
    print("SEARCH RESULTS")
    print(f"  Best R2 found:       {best_r2_overall:.4f}")
    print(f"  Best Residual found: {best_residual_overall:.4f}")
    print(f"  Pareto Candidates:   {len(pareto_candidates)}")
    print("="*70)

    if pareto_candidates:
        print("\nTop Pareto Candidates (Sorted by Residual):")
        sorted_pareto = sorted(pareto_candidates, key=lambda x: x['residual'])
        for cand in sorted_pareto[:5]:
            print(f"  R2: {cand['r2']:.4f} | Residual: {cand['residual']:.4f}")
            print(f"  Assignment: {cand['assignment']}")

if __name__ == "__main__":
    run_multi_objective_search(n_samples=50000)
