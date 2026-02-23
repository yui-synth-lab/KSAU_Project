import numpy as np
import sys
import pandas as pd
from pathlib import Path
from scipy.optimize import differential_evolution
import time

# SSoT Loader Setup
sys.path.insert(0, r"E:\Obsidian\KSAU_Project\ssot")
from ksau_ssot import SSOT

def parse_val(val, default=0.0):
    if pd.isnull(val): return default
    s = str(val).strip()
    if s == "" or s == "undefined" or s == "Not Hyperbolic": return default
    import re
    nums = re.findall(r'-?\d+', s)
    if nums: return float(nums[0])
    return default

def run_fit(data, sectors, kappa):
    # Params: etas (4), intercepts (4), gammas (4), alpha (1), beta (1) = 14 params
    def objective(params):
        etas = {}
        intercepts = {}
        gammas = {}
        for i, s in enumerate(sectors):
            etas[s] = params[i*3]
            intercepts[s] = params[i*3 + 1]
            gammas[s] = params[i*3 + 2]
        
        alpha = params[-2]
        beta = params[-1]
        
        se = []
        for d in data:
            eta = etas[d['s_key']]
            B = intercepts[d['s_key']]
            gamma = gammas[d['s_key']]
            ln_m_pred = eta * kappa * (d['V'] + alpha * d['T'] + beta * d['S'] + gamma * d['K']) + B
            se.append((ln_m_pred - d['ln_m_obs'])**2)
        return np.mean(se)

    bounds = []
    for _ in sectors:
        bounds.extend([(0.1, 30.0), (-50.0, 50.0), (-1.0, 1.0)])
    bounds.extend([(0.0, 1.0), (0.0, 1.0)])
    
    # Using smaller maxiter for speed in FPR test
    res = differential_evolution(objective, bounds, seed=42, strategy='best1bin', maxiter=200)
    
    best_params = res.x
    etas = {}
    intercepts = {}
    gammas = {}
    for i, s in enumerate(sectors):
        etas[s] = best_params[i*3]
        intercepts[s] = best_params[i*3 + 1]
        gammas[s] = best_params[i*3 + 2]
    
    alpha = best_params[-2]
    beta = best_params[-1]
    
    maes = []
    for d in data:
        eta = etas[d['s_key']]
        B = intercepts[d['s_key']]
        gamma = gammas[d['s_key']]
        ln_m_pred = eta * kappa * (d['V'] + alpha * d['T'] + beta * d['S'] + gamma * d['K']) + B
        m_pred = np.exp(ln_m_pred)
        m_obs = np.exp(d['ln_m_obs'])
        err = abs(m_pred - m_obs) / m_obs * 100
        maes.append(err)
    
    return np.mean(maes)

def main():
    ssot = SSOT()
    topo = ssot.topology_assignments()
    knots_df, links_df = ssot.knot_data()
    params = ssot.parameters()
    consts = ssot.constants()
    kappa = consts['mathematical_constants']['kappa']
    
    base_data = []
    for sector_name in ['quarks', 'leptons', 'bosons']:
        for p_name, p_data in params[sector_name].items():
            if p_name not in topo: continue
            info = topo[p_name]
            topo_name = info['topology']
            if "L" in topo_name: match = links_df[links_df['name'] == topo_name]
            else: match = knots_df[knots_df['name'] == topo_name]
            sig = parse_val(match.iloc[0]['signature']) if not match.empty else 0.0
            twist = (2 - info.get('generation', 2)) * ((-1) ** info['components'])
            mass = p_data.get('observed_mass_mev') or p_data.get('observed_mass')
            if not mass: continue
            s_key = sector_name
            if sector_name == "quarks": s_key = f"quarks_c{info['components']}"
            base_data.append({"name": p_name, "V": info['volume'], "C": info['components'], "K": info['crossing_number'], "S": sig, "T": twist, "s_key": s_key, "ln_m_obs": np.log(mass)})

    sectors = sorted(list(set(d['s_key'] for d in base_data)))
    
    obs_mae = run_fit(base_data, sectors, kappa)
    print(f"Observed MAE: {obs_mae:.4f}%")
    
    # Monte Carlo Null Test
    N_TRIALS = 10
    better_than_obs = 0
    print(f"Running {N_TRIALS} Monte Carlo trials with random mass data...")
    
    for i in range(N_TRIALS):
        null_data = []
        for d in base_data:
            nd = d.copy()
            # Randomly sample log mass between -5 and 15 (covering neutrino to top quark range)
            nd['ln_m_obs'] = np.random.uniform(-5, 15)
            null_data.append(nd)
        
        null_mae = run_fit(null_data, sectors, kappa)
        print(f"Trial {i+1}: Null MAE = {null_mae:.4f}%")
        if null_mae <= obs_mae:
            better_than_obs += 1
            
    p_val = better_than_obs / N_TRIALS
    print(f"Approximate p-value (MC): {p_val:.4f}")
    print(f"FPR: {p_val * 100:.1f}%")

if __name__ == "__main__":
    main()
