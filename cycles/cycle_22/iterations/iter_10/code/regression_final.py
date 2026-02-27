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
    
    kappa = consts['mathematical_constants']['kappa']
    G = consts['mathematical_constants']['G_catalan']
    
    # Freeze-out Topologies
    freeze_out = {
        "Electron": {"vol": 0.0,    "det": 3, "c": 1, "gen": 1},
        "Muon":     {"vol": 2.030,  "det": 5, "c": 1, "gen": 2},
        "Tau":      {"vol": 3.164,  "det": 9, "c": 1, "gen": 3},
        "Up":       {"vol": 6.5517, "det": 20, "c": 2, "gen": 1},
        "Down":     {"vol": 7.3277, "det": 16, "c": 3, "gen": 1},
        "Strange":  {"vol": 9.5319, "det": 36, "c": 3, "gen": 2},
        "Charm":    {"vol": 11.4716, "det": 42, "c": 2, "gen": 2},
        "Bottom":   {"vol": 12.2763, "det": 140, "c": 3, "gen": 3},
        "Top":      {"vol": 15.4138, "det": 114, "gen": 3, "c": 2}
    }
    
    data = []
    for p, info in freeze_out.items():
        m_obs = (consts['particle_data']['quarks'][p]['observed_mass'] if p in consts['particle_data']['quarks'] 
                 else consts['particle_data']['leptons'][p]['observed_mass'])
        
        is_lepton = 1 if p in ["Electron", "Muon", "Tau"] else 0
        slope = 20*kappa if is_lepton else (10/7)*G
        twist = (2 - info['gen']) * ((-1)**info['c'])
        
        data.append({
            "particle": p,
            "ln_m": np.log(m_obs),
            "vol": info['vol'],
            "ln_det": np.log(info['det']),
            "c": info['c'],
            "slope": slope,
            "twist": twist,
            "is_lepton": is_lepton
        })
            
    df = pd.DataFrame(data)
    
    # Fit: ln(m) = slope * V + kappa * twist + alpha * ln(det) + gamma * (is_quark) + beta
    df['X1'] = df['slope'] * df['vol']
    df['X2'] = kappa * df['twist']
    df['X3'] = df['ln_det']
    df['X4'] = 1 - df['is_lepton'] # 1 for quarks, 0 for leptons
    
    X = df[['X1', 'X2', 'X3', 'X4']]
    y = df['ln_m']
    
    model = LinearRegression().fit(X, y)
    
    print(f"Regression with Twist and Sector Offset:")
    print(f"Alpha (ln ST): {model.coef_[2]:.6f}")
    print(f"Sector Offset: {model.coef_[3]:.6f}")
    print(f"Beta (Global): {model.intercept_:.6f}")
    print(f"R^2          : {r2_score(y, model.predict(X)):.6f}")

if __name__ == "__main__":
    main()
