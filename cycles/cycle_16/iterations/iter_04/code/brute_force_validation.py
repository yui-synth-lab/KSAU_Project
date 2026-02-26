import sys
import json
import time
import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path
from itertools import product

# SSoT Loader
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
ssot_path = project_root / "ssot"
sys.path.insert(0, str(ssot_path))    
from ksau_ssot import SSOT

def main():
    start_time = time.time()
    ssot = SSOT()
    consts = ssot.constants()
    topology = ssot.topology_assignments()
    params = ssot.parameters()
    kappa = consts['mathematical_constants']['kappa']
    
    data = []
    sectors = ['quarks', 'leptons', 'bosons']
    for sector in sectors:
        p_dict = params[sector]
        for name, meta in p_dict.items():
            if name in topology:
                m_obs = meta['observed_mass_mev']
                topo = topology[name]
                data.append({
                    "name": name,
                    "sector": sector,
                    "v": topo['volume'],
                    "n": float(topo['crossing_number']),
                    "det": float(topo['determinant']),
                    "gen": topo.get('generation', 0),
                    "comp": topo['components'],
                    "ln_m": np.log(m_obs)
                })

    # Brute force parameters
    a_vals = [-1.0, -0.55, 0.0, 0.55, 1.0]
    b_vals = [-1.0, -0.825, 0.0, 0.825, 1.0]
    c_vals = [0.0, 2.75, 5.0]
    nl_vals = [20, 38, 42, 63, 133]
    nb_vals = [3, 5, 7, 10]
    
    best_r2 = -1
    best_params = {}
    
    for a, b, c in product(a_vals, b_vals, c_vals):
        for nl, nb in product(nl_vals, nb_vals):
            # Calculate unified x and y
            x_unified = []
            y_unified = []
            
            for p in data:
                v_eff = p['v'] + a * p['n'] + b * np.log(p['det']) + c
                
                # N selection
                N = 10 if p['sector'] == 'quarks' else (nl if p['sector'] == 'leptons' else nb)
                
                # Twist selection
                # Quarks: (2-Gen)*(-1)^Comp
                # Leptons: Gen-2
                # Bosons: 0
                twist = 0
                if p['sector'] == 'quarks':
                    twist = (2 - p['gen']) * ((-1)**p['comp'])
                elif p['sector'] == 'leptons':
                    twist = p['gen'] - 2
                
                x_unified.append(N * kappa * v_eff)
                y_unified.append(p['ln_m'] - kappa * twist)
                
            _, _, r_v, _, _ = stats.linregress(x_unified, y_unified)
            if r_v**2 > best_r2:
                best_r2 = r_v**2
                best_params = {
                    "a": a, "b": b, "c": c, "nl": nl, "nb": nb
                }

    # Final Test with best params
    a, b, c = best_params['a'], best_params['b'], best_params['c']
    nl, nb = best_params['nl'], best_params['nb']
    
    x_final = []
    y_final = []
    for p in data:
        v_eff = p['v'] + a * p['n'] + b * np.log(p['det']) + c
        N = 10 if p['sector'] == 'quarks' else (nl if p['sector'] == 'leptons' else nb)
        twist = (2 - p['gen']) * ((-1)**p['comp']) if p['sector'] == 'quarks' else (p['gen'] - 2 if p['sector'] == 'leptons' else 0)
        x_final.append(N * kappa * v_eff)
        y_final.append(p['ln_m'] - kappa * twist)
    
    slope, intercept, r_v, p_v, _ = stats.linregress(x_final, y_final)
    
    # FPR with N=10,000
    n_trials = 10000
    null_r2 = []
    np.random.seed(42)
    y_base = np.array(y_final)
    for _ in range(n_trials):
        y_perm = np.random.permutation(y_base)
        _, _, r_perm, _, _ = stats.linregress(x_final, y_perm)
        null_r2.append(r_perm**2)
    fpr = np.sum(np.array(null_r2) >= best_r2) / n_trials
    
    results = {
        "iteration": 4,
        "hypothesis_id": "H40",
        "task_name": "Brute-Force Unified Mass Law Validation",
        "best_r2": float(best_r2),
        "best_p": float(p_v),
        "fpr": float(fpr),
        "best_params": best_params,
        "fitted_slope": float(slope),
        "fitted_intercept": float(intercept),
        "reproducibility": {
            "random_seed": 42,
            "computation_time_sec": time.time() - start_time
        }
    }
    
    with open(current_file.parent.parent / "results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    print(f"Brute force completed. R2 = {best_r2:.6f}, p = {p_v:.2e}, FPR = {fpr:.4f}")
    print(f"Best parameters: {best_params}")

if __name__ == "__main__":
    main()
