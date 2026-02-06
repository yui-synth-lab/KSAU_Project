"""
KSAU v3.3 Compliant Brute-Force Verification (Portable Version)
------------------------------------------------------------------
Implements the Component-Charge Symmetry rule and saves results to JSON.
"""

import pandas as pd
import numpy as np
from scipy.optimize import minimize
from tqdm import tqdm
import json
import os

# Relative paths for portability
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Note: In the publish package, data is in ../../data/ (shared) or ../data/ (v3.3 specific)
# We assume the user has the linkinfo database in the standard publish/data location
DATA_PATH = os.path.join(BASE_DIR, "..", "..", "data", "linkinfo_data_complete.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "..", "data", "brute_force_v3_3_results.json")

QUARK_MASSES = {'u': 2.16, 'd': 4.67, 's': 93.4, 'c': 1270, 'b': 4180, 't': 172760}
REPORTED_QUARKS_V33 = {
    'u': 'L7a5', 'd': 'L6a4', 's': 'L11n345', 'c': 'L11n64', 'b': 'L10a141', 't': 'L11a62'
}

def fit_quarks_log(volumes, masses):
    V = np.array(volumes)
    ln_m_obs = np.log(masses)
    def objective(params):
        gamma, b_prime = params
        ln_m_pred = gamma * V + b_prime
        return np.sum((ln_m_obs - ln_m_pred)**2)
    res = minimize(objective, x0=[1.3, -7.0], method='Nelder-Mead')
    gamma, b_prime = res.x
    ln_m_pred = gamma * V + b_prime
    m_pred = np.exp(ln_m_pred)
    ss_res = np.sum((ln_m_obs - ln_m_pred)**2)
    ss_tot = np.sum((ln_m_obs - np.mean(ln_m_obs))**2)
    r2 = 1 - (ss_res / ss_tot)
    mae_pct = np.mean(np.abs((m_pred - masses) / masses)) * 100
    return r2, mae_pct

def load_data():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Database not found at {DATA_PATH}. Ensure the data directory is present.")
    df = pd.read_csv(DATA_PATH, sep='|', low_memory=False, skiprows=[1])
    df['components_num'] = pd.to_numeric(df['components'], errors='coerce')
    df['Vol'] = pd.to_numeric(df['volume'], errors='coerce')
    links = df[df['components_num'].isin([2, 3])].copy()
    links = links[links['Vol'] > 0].copy()
    links = links.drop_duplicates('name').reset_index(drop=True)
    return links

def main():
    print(f"Loading link database from: {DATA_PATH}")
    links = load_data()
    vols_v33 = []
    for q in ['u', 'd', 's', 'c', 'b', 't']:
        base = REPORTED_QUARKS_V33[q]
        match = links[links['name'].str.startswith(base)]
        vols_v33.append(match.iloc[0]['Vol'])
    
    r2_33, _ = fit_quarks_log(vols_v33, [QUARK_MASSES[q] for q in ['u', 'd', 's', 'c', 'b', 't']])
    
    n_samples = 10000
    print(f"Verified KSAU v3.3 R^2: {r2_33:.6f}")
    print(f"Sampling {n_samples} trials within Component-Charge Symmetry...")
    l2 = links[links['components_num'] == 2]['Vol'].values
    l3 = links[links['components_num'] == 3]['Vol'].values
    q_masses = np.array([QUARK_MASSES[q] for q in ['u', 'd', 's', 'c', 'b', 't']])
    
    results_r2 = []
    for _ in tqdm(range(n_samples)):
        idx2 = np.random.choice(len(l2), 3, replace=False)
        idx3 = np.random.choice(len(l3), 3, replace=False)
        v = np.array([l2[idx2[0]], l3[idx3[0]], l3[idx3[1]], l2[idx2[1]], l3[idx3[2]], l2[idx2[2]]])
        r2, _ = fit_quarks_log(v, q_masses)
        results_r2.append(float(r2))

    with open(OUTPUT_PATH, 'w') as f:
        json.dump({'reported_r2': r2_33, 'random_r2_values': results_r2}, f)
    print(f"\nVerification complete. Results saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()