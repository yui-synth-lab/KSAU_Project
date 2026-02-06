"""
KSAU v3.4 Robustness Analysis
-----------------------------
Implements the critical requirements for v3.4 validation:
1. Full Refit with L10n95 (Strange)
2. Bootstrap Analysis (10k iterations) for 95% CIs
3. Leave-One-Out (LOO) Cross-Validation
4. Top-K Candidate Tables for all quarks

Usage:
    python ksau_v3_4_robustness.py
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
OUTPUT_REPORT = os.path.join(BASE_DIR, "..", "data", "v3_4_robustness_report.txt")

# Physical Constants (MeV)
QUARK_MASSES = {'u': 2.16, 'd': 4.67, 's': 93.4, 'c': 1270, 'b': 4180, 't': 172760}

# v3.4 Candidate Assignment
ASSIGNMENT_V34 = {
    'u': 'L7a5',      # 2-comp
    'd': 'L6a4',      # 3-comp
    's': 'L10n95',    # 3-comp (NEW v3.4 Candidate)
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
    vol_map = {}
    for q, name in assignment.items():
        # Exact match or prefix match logic
        matches = full_df[full_df['name'] == name]
        if len(matches) == 0:
             matches = full_df[full_df['name'].str.startswith(name + '{')]
        if len(matches) == 0:
             matches = full_df[full_df['name'].str.startswith(name)]
             
        if len(matches) == 0:
            raise ValueError(f"Link {name} not found in database.")
        
        vol_map[q] = matches.iloc[0]['Vol']
    return vol_map

def fit_ols(volumes, masses):
    """
    Fits ln(m) = gamma * V + b'
    Returns: r2, mae_pct, gamma, b_prime, residuals
    """
    V = np.array(volumes)
    ln_m = np.log(np.array(masses))
    
    A = np.vstack([V, np.ones(len(V))]).T
    gamma, b_prime = np.linalg.lstsq(A, ln_m, rcond=None)[0]
    
    ln_m_pred = gamma * V + b_prime
    m_pred = np.exp(ln_m_pred)
    
    ss_res = np.sum((ln_m - ln_m_pred)**2)
    ss_tot = np.sum((ln_m - np.mean(ln_m))**2)
    r2 = 1 - (ss_res / ss_tot)
    
    mae_pct = np.mean(np.abs((m_pred - masses) / masses)) * 100
    residuals = ln_m - ln_m_pred
    
    return r2, mae_pct, gamma, b_prime, residuals

def bootstrap_ci(volumes, masses, n_boot=10000):
    """Residual Bootstrapping"""
    V = np.array(volumes)
    ln_m_obs = np.log(np.array(masses))
    
    # Original Fit
    _, mae_orig, gamma_hat, b_hat, residuals = fit_ols(V, masses)
    ln_m_pred = gamma_hat * V + b_hat
    
    gammas, b_primes, maes = [], [], []
    
    for _ in range(n_boot):
        res_boot = np.random.choice(residuals, size=len(residuals), replace=True)
        ln_m_boot = ln_m_pred + res_boot
        m_boot_virtual = np.exp(ln_m_boot) # For MAE calculation
        
        # Refit
        A = np.vstack([V, np.ones(len(V))]).T
        g, b = np.linalg.lstsq(A, ln_m_boot, rcond=None)[0]
        
        # Calculate MAE for this bootstrap sample (against original masses or virtual? 
        # Standard residual bootstrap usually estimates parameter uncertainty. 
        # For prediction error distribution, we look at parameter variation.)
        
        gammas.append(g)
        b_primes.append(b)
        
        # Re-calculate MAE of the *model* (with bootstrapped params) against *original* data
        # to see stability of the fit quality
        ln_m_pred_boot = g * V + b
        m_pred_boot = np.exp(ln_m_pred_boot)
        mae_boot = np.mean(np.abs((m_pred_boot - masses) / masses)) * 100
        maes.append(mae_boot)
        
    return {
        'gamma': (np.mean(gammas), np.percentile(gammas, [2.5, 97.5])),
        'b': (np.mean(b_primes), np.percentile(b_primes, [2.5, 97.5])),
        'mae': (np.mean(maes), np.percentile(maes, [2.5, 97.5]))
    }

def loo_cv(volumes, masses):
    """Leave-One-Out Cross Validation"""
    errors = []
    quarks = list(QUARK_MASSES.keys()) # ['u', 'd', 's', 'c', 'b', 't']
    
    print("\n--- LOO Cross-Validation Results ---")
    print(f"{'Excluded':<5} {'Actual':<10} {'Pred':<10} {'Error %':<10}")
    
    for i in range(len(volumes)):
        # Train on all except i
        v_train = np.delete(volumes, i)
        m_train = np.delete(masses, i)
        
        _, _, gamma, b_prime, _ = fit_ols(v_train, m_train)
        
        # Test on i
        ln_m_pred = gamma * volumes[i] + b_prime
        m_pred = np.exp(ln_m_pred)
        
        actual = masses[i]
        err_pct = (m_pred - actual) / actual * 100
        errors.append(abs(err_pct))
        
        print(f"{quarks[i]:<5} {actual:<10.2f} {m_pred:<10.2f} {err_pct:>+8.2f}%")
        
    return np.mean(errors)

def find_top_k(target_q, pool, current_assignment, full_df, k=5):
    """Finds top k alternatives for a specific quark slot"""
    base_vols = get_volume_map(current_assignment, full_df)
    
    # We want to vary target_q while keeping others fixed
    fixed_qs = [q for q in QUARK_MASSES if q != target_q]
    fixed_vols = [base_vols[q] for q in fixed_qs]
    fixed_masses = [QUARK_MASSES[q] for q in fixed_qs]
    target_mass = QUARK_MASSES[target_q]
    
    results = []
    for _, row in pool.iterrows():
        trial_vols = fixed_vols + [row['Vol']]
        trial_masses = fixed_masses + [target_mass]
        
        # Note: fit_ols order doesn't matter for R2/MAE if lists are aligned
        r2, mae, _, _, _ = fit_ols(trial_vols, trial_masses)
        results.append((row['name'], row['Vol'], mae, r2))
        
    results.sort(key=lambda x: x[2]) # Sort by MAE
    return results[:k]

def main():
    pool_2, pool_3, df = load_data()
    
    # 1. Prepare Data
    vol_map = get_volume_map(ASSIGNMENT_V34, df)
    # Ensure ordered lists strictly matching QUARK_MASSES keys order for consistency
    q_order = ['u', 'd', 's', 'c', 'b', 't']
    vols = [vol_map[q] for q in q_order]
    masses = [QUARK_MASSES[q] for q in q_order]
    
    report = []
    report.append("KSAU v3.4 Robustness Report")
    report.append("===========================")
    
    # 2. Full Fit
    r2, mae, gamma, b_prime, _ = fit_ols(vols, masses)
    report.append(f"\n[1] Full Fit (v3.4 Candidate)")
    report.append(f"Assignment: {ASSIGNMENT_V34}")
    report.append(f"R^2: {r2:.6f}")
    report.append(f"MAE: {mae:.4f}%")
    report.append(f"Gamma: {gamma:.4f}")
    report.append(f"B': {b_prime:.4f}")
    
    # 3. Bootstrap
    report.append(f"\n[2] Bootstrap Analysis (N=10000)")
    boot = bootstrap_ci(vols, masses, n_boot=10000)
    report.append(f"Gamma 95% CI: [{boot['gamma'][1][0]:.4f}, {boot['gamma'][1][1]:.4f}] (Mean: {boot['gamma'][0]:.4f})")
    report.append(f"B' 95% CI:    [{boot['b'][1][0]:.4f}, {boot['b'][1][1]:.4f}] (Mean: {boot['b'][0]:.4f})")
    report.append(f"MAE 95% CI:   [{boot['mae'][1][0]:.4f}%, {boot['mae'][1][1]:.4f}%]")
    
    # 4. LOO-CV
    report.append(f"\n[3] LOO Cross-Validation")
    # Redirect stdout to capture LOO details if needed, but for now just run it
    # We will print details to console and summary to report
    loo_mae = loo_cv(vols, masses)
    report.append(f"LOO Mean Absolute Error: {loo_mae:.4f}%")
    
    # 5. Top-K Tables
    report.append(f"\n[4] Top-5 Candidates Per Quark (Uniqueness Check)")
    
    for q in q_order:
        comp_target = 2 if q in ['u', 'c', 't'] else 3
        pool = pool_2 if comp_target == 2 else pool_3
        
        top_k = find_top_k(q, pool, ASSIGNMENT_V34, df, k=5)
        
        report.append(f"\n-- {q.upper()} Quark (Comp={comp_target}) --")
        report.append(f"{'Rank':<5} {'Name':<15} {'Vol':<10} {'MAE %':<10}")
        for i, (name, vol, k_mae, k_r2) in enumerate(top_k):
            marker = "*" if name == ASSIGNMENT_V34[q] or name.startswith(ASSIGNMENT_V34[q]+"{") else ""
            report.append(f"{i+1:<5} {name:<15} {vol:<10.4f} {k_mae:<10.4f} {marker}")
            
    # Save
    with open(OUTPUT_REPORT, 'w') as f:
        f.write('\n'.join(report))
        
    print(f"\nAnalysis complete. Report written to {OUTPUT_REPORT}")
    print('\n'.join(report))

if __name__ == "__main__":
    main()
