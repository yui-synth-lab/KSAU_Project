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
    hbar = consts['physical_constants']['h_bar_mev_s']
    # Planck Mass in MeV
    M_P = 1.0 / np.sqrt(G_ksau)
    
    kappa = consts['mathematical_constants']['kappa']
    pi = consts['mathematical_constants']['pi']
    
    # 2. KSAU Dimensional Mapping
    # Base Action S_0 = 14 * pi * hbar
    # KSAU Mass Scale M_ksau = M_P * exp(-S_0/hbar)
    S_0_hbar = 14 * pi
    M_ksau = M_P * np.exp(-S_0_hbar)
    
    # alpha from H62
    alpha = np.sqrt(2) * kappa
    
    # 3. Data Preparation
    data = []
    for p, entry in assignments.items():
        if p in consts['particle_data']['quarks']:
            m_obs = consts['particle_data']['quarks'][p]['observed_mass']
            is_confined = True
        elif p in consts['particle_data']['leptons']:
            m_obs = consts['particle_data']['leptons'][p]['observed_mass']
            is_confined = False
        elif p in consts['particle_data']['bosons']:
            m_obs = consts['particle_data']['bosons'][p]['observed_mass']
            is_confined = False
        else: continue
            
        data.append({
            "particle": p,
            "m_obs": m_obs,
            "ln_m_obs": np.log(m_obs),
            "V": entry['volume'],
            "c": entry['components'],
            "det": entry['determinant'],
            "s": entry['signature'],
            "n": entry['crossing_number'],
            "is_confined": is_confined
        })
    df = pd.DataFrame(data)
    
    # 4. Geometric Potential Phi
    # Slope factor eta = 6*pi / c
    df['eta'] = (6 * pi) / df['c']
    
    # Torsion term T
    pi_alpha = pi / alpha
    df['T'] = np.log(df['det']) + df['s'] - df['n'] - pi_alpha * np.log(df['c'])
    
    # Confined Shift (Quarks)
    # Based on previous analysis, Quarks have an additional 2*pi (c=2) or 1*pi (c=3) suppression?
    # Let's test a simple shift: Delta_S = (4 - c) * pi for confined particles.
    df['delta_phi'] = np.where(df['is_confined'], -(4 - df['c']) * pi, 0.0)
    
    # Predicted ln(m)
    # ln(m) = ln(M_ksau) + Phi
    # Phi = eta * kappa * V + alpha * T + delta_phi
    df['Phi'] = df['eta'] * kappa * df['V'] + alpha * df['T'] + df['delta_phi']
    df['ln_m_pred'] = np.log(M_ksau) + df['Phi']
    
    # 5. Evaluation
    r2 = r2_score(df['ln_m_obs'], df['ln_m_pred'])
    df['m_pred'] = np.exp(df['ln_m_pred'])
    df['error_pct'] = (df['m_pred'] - df['m_obs']) / df['m_obs'] * 100
    
    print(f"M_P: {M_P:.4e} MeV")
    print(f"M_ksau: {M_ksau:.4f} MeV")
    print(f"Model R2: {r2:.6f}")
    print("-" * 100)
    print(f"{'Particle':10} | {'Obs (MeV)':10} | {'Pred (MeV)':10} | {'Error %':10} | {'Phi':10}")
    print("-" * 100)
    for _, row in df.iterrows():
        print(f"{row['particle']:10} | {row['m_obs']:10.2f} | {row['m_pred']:10.2f} | {row['error_pct']:9.2f}% | {row['Phi']:10.4f}")
        
    results = {
        "M_P_MeV": M_P,
        "M_ksau_MeV": M_ksau,
        "S_0_hbar": S_0_hbar,
        "r2": r2,
        "predictions": df.to_dict(orient='records')
    }
    
    with open(project_root / "cycles/cycle_24/iterations/iter_05/results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
