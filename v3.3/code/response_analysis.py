"""
KSAU v3.3 Response Analysis: Uniqueness & Robustness
----------------------------------------------------
Addressing Critique:
1. Is L11n345 (Strange) unique? (Top-K Analysis)
2. Is L11n64 (Charm) unique? (Top-K Analysis)
3. Confidence Intervals (Bootstrap)

Usage:
    python response_analysis.py
"""

import pandas as pd
import numpy as np
from scipy.optimize import minimize
import json
import os
import sys

# Setup Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "..", "data", "linkinfo_data_complete.csv")
OUTPUT_JSON = os.path.join(BASE_DIR, "..", "data", "response_analysis_results.json")
OUTPUT_REPORT = os.path.join(BASE_DIR, "..", "data", "response_analysis_report.txt")

# Physical Constants
QUARK_MASSES = {'u': 2.16, 'd': 4.67, 's': 93.4, 'c': 1270, 'b': 4180, 't': 172760}

# The v3.3 "Discovery" Assignment
ASSIGNMENT_V33 = {
    'u': 'L7a5',      # 2-comp
    'd': 'L6a4',      # 3-comp
    's': 'L11n345',   # 3-comp (Target of critique)
    'c': 'L11n64',    # 2-comp
    'b': 'L10a141',   # 3-comp
    't': 'L11a62'     # 2-comp
}

def load_data():
    if not os.path.exists(DATA_PATH):
        print(f"Error: Data file not found at {DATA_PATH}")
        sys.exit(1)
    
    print(f"Loading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH, sep='|', low_memory=False, skiprows=[1])
    
    # Clean and Filter
    df['components_num'] = pd.to_numeric(df['components'], errors='coerce')
    df['Vol'] = pd.to_numeric(df['volume'], errors='coerce')
    df = df[df['Vol'] > 0].dropna(subset=['components_num', 'Vol', 'name'])
    
    # Separate pools
    pool_2comp = df[df['components_num'] == 2].copy().reset_index(drop=True)
    pool_3comp = df[df['components_num'] == 3].copy().reset_index(drop=True)
    
    print(f"Pool Sizes: 2-comp={len(pool_2comp)}, 3-comp={len(pool_3comp)}")
    return pool_2comp, pool_3comp, df

def get_volume_map(assignment, full_df):
    """Converts a name map {'u': 'L7a5'...} to a volume map {'u': 6.60...}"""
    vol_map = {}
    for q, name in assignment.items():
        # Match name or name{...}
        matches = full_df[full_df['name'].str.startswith(name)]
        if len(matches) == 0:
            # Try appending '{' just in case name is a prefix of another link name
            matches = full_df[full_df['name'].str.startswith(name + '{')]
        
        if len(matches) == 0:
             # Exact match fallback
            matches = full_df[full_df['name'] == name]

        if len(matches) == 0:
            raise ValueError(f"Link {name} not found in database.")
        
        # Take the first match's volume (assuming volume is invariant across orientations/components)
        vol_map[q] = matches.iloc[0]['Vol']
    return vol_map

def fit_model(volumes, masses):
    """Fits ln(m) = gamma * V + b'. Returns R2, MAE%, gamma, b'."""
    V = np.array(volumes)
    ln_m = np.log(np.array(masses))
    
    # OLS Solution for y = ax + b
    A = np.vstack([V, np.ones(len(V))]).T
    gamma, b_prime = np.linalg.lstsq(A, ln_m, rcond=None)[0]
    
    ln_m_pred = gamma * V + b_prime
    m_pred = np.exp(ln_m_pred)
    
    ss_res = np.sum((ln_m - ln_m_pred)**2)
    ss_tot = np.sum((ln_m - np.mean(ln_m))**2)
    r2 = 1 - (ss_res / ss_tot)
    
    # MAE Percentage
    mae_pct = np.mean(np.abs((m_pred - masses) / masses)) * 100
    
    return r2, mae_pct, gamma, b_prime

def analyze_perturbation(target_quark, pool, current_assignment, full_df):
    """
    Varies 'target_quark' across ALL links in 'pool'.
    Keeps other quarks fixed to 'current_assignment'.
    Returns sorted list of top candidates.
    """
    base_vols = get_volume_map(current_assignment, full_df)
    results = []
    
    # Prepare fixed data
    fixed_quarks = [q for q in QUARK_MASSES.keys() if q != target_quark]
    fixed_vols = [base_vols[q] for q in fixed_quarks]
    fixed_masses = [QUARK_MASSES[q] for q in fixed_quarks]
    target_mass = QUARK_MASSES[target_quark]
    
    print(f"Scanning {len(pool)} candidates for {target_quark}...")
    
    for _, row in pool.iterrows():
        # Construct trial dataset
        trial_vols = fixed_vols + [row['Vol']]
        trial_masses = fixed_masses + [target_mass]
        
        r2, mae, _, _ = fit_model(trial_vols, trial_masses)
        
        results.append({
            'name': row['name'],
            'vol': row['Vol'],
            'r2': r2,
            'mae': mae
        })
        
    # Sort by MAE (lower is better)
    results.sort(key=lambda x: x['mae'])
    return results[:10]  # Return top 10

def bootstrap_analysis(assignment, full_df, n_boot=10000):
    """
    Performs residual bootstrapping to estimate CI for gamma and b'.
    """
    vol_map = get_volume_map(assignment, full_df)
    vols = np.array([vol_map[q] for q in ['u', 'd', 's', 'c', 'b', 't']])
    masses = np.array([QUARK_MASSES[q] for q in ['u', 'd', 's', 'c', 'b', 't']])
    ln_m_obs = np.log(masses)
    
    # Initial Fit
    r2, mae, gamma_hat, b_hat = fit_model(vols, masses)
    ln_m_pred = gamma_hat * vols + b_hat
    residuals = ln_m_obs - ln_m_pred
    
    gammas = []
    b_primes = []
    
    for _ in range(n_boot):
        # Resample residuals with replacement
        res_boot = np.random.choice(residuals, size=len(residuals), replace=True)
        ln_m_boot = ln_m_pred + res_boot
        
        # Refit
        A = np.vstack([vols, np.ones(len(vols))]).T
        g, b = np.linalg.lstsq(A, ln_m_boot, rcond=None)[0]
        gammas.append(g)
        b_primes.append(b)
        
    ci_gamma = np.percentile(gammas, [2.5, 97.5])
    ci_b = np.percentile(b_primes, [2.5, 97.5])
    
    return {
        'gamma_mean': np.mean(gammas),
        'gamma_ci': ci_gamma.tolist(),
        'b_mean': np.mean(b_primes),
        'b_ci': ci_b.tolist(),
        'n_boot': n_boot
    }

def main():
    pool_2, pool_3, df = load_data()
    
    report_lines = []
    report_lines.append("KSAU v3.3 Response Analysis Report")
    report_lines.append("==================================")
    
    # 1. Verify Baseline
    vols = get_volume_map(ASSIGNMENT_V33, df)
    # Ensure ordered lists
    ordered_quarks = list(vols.keys())
    ordered_vols = [vols[q] for q in ordered_quarks]
    ordered_masses = [QUARK_MASSES[q] for q in ordered_quarks]
    
    r2, mae, _, _ = fit_model(ordered_vols, ordered_masses)
    report_lines.append(f"Baseline (v3.3) MAE: {mae:.2f}% | R2: {r2:.6f}")
    report_lines.append("")
    
    # 2. Strange Quark Analysis (3-component pool)
    report_lines.append("--- Experiment A: Uniqueness of Strange (L11n345) ---")
    top_s = analyze_perturbation('s', pool_3, ASSIGNMENT_V33, df)
    report_lines.append(f"{'Rank':<5} {'Name':<12} {'Vol':<8} {'MAE(%)':<8} {'R2':<8}")
    for i, res in enumerate(top_s):
        report_lines.append(f"{i+1:<5} {res['name']:<12} {res['vol']:<8.4f} {res['mae']:<8.3f} {res['r2']:.6f}")
    
    # Check rank of reported link
    ranks = [i+1 for i, r in enumerate(top_s) if r['name'] == 'L11n345']
    s_rank = ranks[0] if ranks else ">10"
    report_lines.append(f"Reported L11n345 Rank: {s_rank}")
    report_lines.append("")
    
    # 3. Charm Quark Analysis (2-component pool)
    report_lines.append("--- Experiment B: Uniqueness of Charm (L11n64) ---")
    top_c = analyze_perturbation('c', pool_2, ASSIGNMENT_V33, df)
    report_lines.append(f"{'Rank':<5} {'Name':<12} {'Vol':<8} {'MAE(%)':<8} {'R2':<8}")
    for i, res in enumerate(top_c):
        report_lines.append(f"{i+1:<5} {res['name']:<12} {res['vol']:<8.4f} {res['mae']:<8.3f} {res['r2']:.6f}")
        
    ranks = [i+1 for i, r in enumerate(top_c) if r['name'] == 'L11n64']
    c_rank = ranks[0] if ranks else ">10"
    report_lines.append(f"Reported L11n64 Rank: {c_rank}")
    report_lines.append("")
    
    # 4. Bootstrap CIs
    report_lines.append("--- Experiment C: Bootstrap Confidence Intervals ---")
    boot_res = bootstrap_analysis(ASSIGNMENT_V33, df)
    report_lines.append(f"Bootstrap Samples: {boot_res['n_boot']}")
    report_lines.append(f"Slope (gamma): {boot_res['gamma_mean']:.4f} [95% CI: {boot_res['gamma_ci'][0]:.4f} - {boot_res['gamma_ci'][1]:.4f}]")
    report_lines.append(f"Intercept (b'): {boot_res['b_mean']:.4f} [95% CI: {boot_res['b_ci'][0]:.4f} - {boot_res['b_ci'][1]:.4f}]")
    
    # Save Report
    with open(OUTPUT_REPORT, 'w') as f:
        f.write('\n'.join(report_lines))
    
    # Save JSON data
    full_data = {
        'baseline': {'mae': mae, 'r2': r2},
        'top_strange': top_s,
        'top_charm': top_c,
        'bootstrap': boot_res
    }
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(full_data, f, indent=2)
        
    print(f"\nAnalysis Complete. Report saved to {OUTPUT_REPORT}")
    print('\n'.join(report_lines))

if __name__ == "__main__":
    main()
