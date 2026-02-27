import sys
from pathlib import Path
import numpy as np
import pandas as pd
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
    alpha = -3.85
    
    strategy_c = {
        "Electron": {"vol": 0.0,    "det": 3, "slope": 20*kappa},
        "Muon":     {"vol": 2.030,  "det": 5, "slope": 20*kappa},
        "Tau":      {"vol": 3.164,  "det": 9, "slope": 20*kappa},
        "Up":       {"vol": 5.083,  "det": 22, "slope": 10*kappa},
        "Down":     {"vol": 5.333,  "det": 12, "slope": 10*kappa},
        "Strange":  {"vol": 9.665,  "det": 36, "slope": 10*kappa},
        "Charm":    {"vol": 9.707,  "det": 48, "slope": 10*kappa},
        "Bottom":   {"vol": 13.602, "det": 60, "slope": 10*kappa},
        "Top":      {"vol": 14.963, "det": 90, "slope": 10*kappa}
    }
    
    data = []
    for p, entry in strategy_c.items():
        m_obs = (consts['particle_data']['quarks'][p]['observed_mass'] if p in consts['particle_data']['quarks'] 
                 else consts['particle_data']['leptons'][p]['observed_mass'])
        data.append({
            "particle": p,
            "ln_m": np.log(m_obs),
            "vol": entry['vol'],
            "ln_det": np.log(entry['det']),
            "slope": entry['slope']
        })
            
    df = pd.DataFrame(data)
    
    y_corr = df['ln_m'] - df['slope'] * df['vol'] - alpha * df['ln_det']
    beta = np.mean(y_corr)
    
    df['ln_m_pred'] = df['slope'] * df['vol'] + alpha * df['ln_det'] + beta
    r2 = r2_score(df['ln_m'], df['ln_m_pred'])
    
    print(f"Unified Intercept Model (Strategy C):")
    print(f"Alpha: {alpha:.6f}, Beta: {beta:.6f}")
    print(f"R^2  : {r2:.6f}")

if __name__ == "__main__":
    main()
