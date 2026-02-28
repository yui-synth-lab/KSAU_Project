import sys
from pathlib import Path
import numpy as np
import pandas as pd
import json
from sklearn.metrics import r2_score

# SSoT Loading
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
ssot_path = project_root / "ssot"
sys.path.insert(0, str(ssot_path))    
from ksau_ssot import SSOT

def main():
    ssot = SSOT()
    consts = ssot.constants()
    assignments = ssot.topology_assignments()
    
    # 1. Physical Constants
    G_ksau = consts['gravity']['G_ksau']
    M_P = 1.0 / np.sqrt(G_ksau)
    kappa = consts['mathematical_constants']['kappa']
    pi = consts['mathematical_constants']['pi']
    
    # SSoT parameters
    alpha = np.sqrt(2) * kappa
    gamma = -consts['topology_constants']['v_borromean']
    
    # Sector slopes from SSoT
    eta_map = {
        "leptons":   consts['phase_viscosity_model']['sectors']['leptons']['eta'],
        "quarks_c2": consts['phase_viscosity_model']['sectors']['quarks_c2']['eta'],
        "quarks_c3": consts['phase_viscosity_model']['sectors']['quarks_c3']['eta'],
        "bosons":    consts['phase_viscosity_model']['sectors']['bosons']['eta']
    }
    
    # 2. Data Preparation
    data = []
    for name, entry in assignments.items():
        m_obs = None
        sector = None
        if name in consts['particle_data']['quarks']:
            m_obs = consts['particle_data']['quarks'][name]['observed_mass']
            sector = f"quarks_c{entry['components']}"
        elif name in consts['particle_data']['leptons']:
            m_obs = consts['particle_data']['leptons'][name]['observed_mass']
            sector = "leptons"
        elif name in consts['particle_data']['bosons']:
            m_obs = consts['particle_data']['bosons'][name]['observed_mass']
            sector = "bosons"
        
        if m_obs is None: continue
        
        data.append({
            "name": name,
            "m_obs": m_obs,
            "ln_m_obs": np.log(m_obs),
            "V": entry['volume'],
            "n": entry['crossing_number'],
            "c": entry['components'],
            "det": entry['determinant'],
            "s": entry['signature'],
            "eta": eta_map[sector]
        })
    df = pd.DataFrame(data)
    
    # 3. Model
    # ln(m/MeV) = eta * kappa * V + alpha * T + gamma + beta
    # T from Iter 7: ln(det) + s - n
    # But wait, H62 Iter 4 used: T = ln(det) + s - n - (pi/alpha)*ln(c)
    pi_alpha = pi / alpha
    df['T'] = np.log(df['det']) + df['s'] - df['n'] - pi_alpha * np.log(df['c'])
    
    df['base_pred'] = df['eta'] * kappa * df['V'] + alpha * df['T'] + gamma
    
    # Find best beta
    beta_est = np.mean(df['ln_m_obs'] - df['base_pred'])
    
    df['ln_m_pred'] = df['base_pred'] + beta_est
    df['m_pred'] = np.exp(df['ln_m_pred'])
    df['error_pct'] = (df['m_pred'] - df['m_obs']) / df['m_obs'] * 100
    
    r2 = r2_score(df['ln_m_obs'], df['ln_m_pred'])
    
    print(f"SSoT-Compatible Model (Beta={beta_est:.4f})")
    print(f"R2 (12 particles): {r2:.6f}")
    print("-" * 80)
    print(f"{'Particle':10} | {'Obs (MeV)':10} | {'Pred (MeV)':10} | {'Error %'}")
    print("-" * 80)
    for _, row in df.iterrows():
        print(f"{row['name']:10} | {row['m_obs']:10.2f} | {row['m_pred']:10.2f} | {row['error_pct']:8.2f}%")

    # FPR Check
    np.random.seed(42)
    n_trials = 10000
    hits = 0
    obs_mae = np.mean(np.abs(df['ln_m_obs'] - df['ln_m_pred']))
    
    indices = np.arange(len(df))
    for _ in range(n_trials):
        # Shuffle assignments of (V, n, c, det, s, eta) to (name, m_obs)
        perm = np.random.permutation(indices)
        perm_V = df['V'].values[perm]
        perm_n = df['n'].values[perm]
        perm_c = df['c'].values[perm]
        perm_det = df['det'].values[perm]
        perm_s = df['s'].values[perm]
        perm_eta = df['eta'].values[perm]
        
        perm_T = np.log(perm_det) + perm_s - perm_n - pi_alpha * np.log(perm_c)
        perm_base = perm_eta * kappa * perm_V + alpha * perm_T + gamma
        # Note: beta should be re-estimated for each permutation to be fair?
        # Actually, beta is a "global scaling" allowed by H63.
        perm_beta = np.mean(df['ln_m_obs'] - perm_base)
        perm_pred = perm_base + perm_beta
        perm_mae = np.mean(np.abs(df['ln_m_obs'] - perm_pred))
        
        if perm_mae <= obs_mae:
            hits += 1
    fpr = hits / n_trials
    print(f"FPR: {fpr:.4f}")

    results = {
        "beta": float(beta_est),
        "r2": float(r2),
        "fpr": float(fpr),
        "particles": df[['name', 'm_obs', 'm_pred', 'error_pct']].to_dict(orient='records')
    }
    
    with open(project_root / "cycles/cycle_24/iterations/iter_08/results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
