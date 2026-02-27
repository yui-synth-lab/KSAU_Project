import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# AIRDP SSoT Loader setup
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
ssot_path = project_root / "ssot"
sys.path.insert(0, str(ssot_path))    
from ksau_ssot import SSOT

def main():
    ssot = SSOT()
    consts = ssot.constants()
    assignments = ssot.topology_assignments()
    
    kappa = consts['mathematical_constants']['kappa'] # pi/24
    alpha_fixed = kappa**2 # Derived in this iteration
    
    # 9 Fermions
    particles = [
        "Electron", "Muon", "Tau",
        "Up", "Down", "Charm", "Strange", "Top", "Bottom"
    ]
    
    data = []
    for p in particles:
        if p in assignments:
            entry = assignments[p]
            if p in consts['particle_data']['quarks']:
                m_obs = consts['particle_data']['quarks'][p]['observed_mass']
                sector = 'quark'
            elif p in consts['particle_data']['leptons']:
                m_obs = consts['particle_data']['leptons'][p]['observed_mass']
                sector = 'lepton'
            else:
                continue
                
            data.append({
                "particle": p,
                "sector": sector,
                "m_obs": m_obs,
                "ln_m": np.log(m_obs),
                "vol": entry['volume'],
                "ln_det": np.log(entry['determinant']) if entry['determinant'] > 0 else 0
            })
            
    df = pd.DataFrame(data)
    
    # Sector-specific Fitted Slopes (alpha = kappa^2)
    # Quarks
    q_df = df[df['sector'] == 'quark'].copy()
    X_q = q_df[['vol']].values
    y_q = q_df['ln_m'] - alpha_fixed * q_df['ln_det']
    model_q = LinearRegression().fit(X_q, y_q)
    S_q = model_q.coef_[0]
    C_q = model_q.intercept_
    
    # Leptons
    l_df = df[df['sector'] == 'lepton'].copy()
    X_l = l_df[['vol']].values
    y_l = l_df['ln_m'] - alpha_fixed * l_df['ln_det']
    model_l = LinearRegression().fit(X_l, y_l)
    S_l = model_l.coef_[0]
    C_l = model_l.intercept_
    
    # Combine predictions
    df['y_pred'] = 0.0
    for idx, row in df.iterrows():
        if row['sector'] == 'lepton':
            df.at[idx, 'y_pred'] = S_l * row['vol'] + alpha_fixed * row['ln_det'] + C_l
        else:
            df.at[idx, 'y_pred'] = S_q * row['vol'] + alpha_fixed * row['ln_det'] + C_q
            
    r2_total = r2_score(df['ln_m'], df['y_pred'])
    print(f"Preliminary Validation Result:")
    print(f"Total R^2 (2 sectors): {r2_total:.6f}")
    print(f"Quark Slope S_q      : {S_q:.6f}")
    print(f"Lepton Slope S_l     : {S_l:.6f}")

if __name__ == "__main__":
    main()
