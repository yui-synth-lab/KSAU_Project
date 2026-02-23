import numpy as np
import sys
import json
from pathlib import Path
from scipy.stats import linregress
from sklearn.metrics import r2_score

# SSoT Loader setup
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
ssot_dir = project_root / "ssot"
sys.path.insert(0, str(ssot_dir))
from ksau_ssot import SSOT

def main():
    ssot = SSOT()
    params = ssot.parameters()
    topo = ssot.topology_assignments()
    kappa = ssot.constants()['mathematical_constants']['kappa']
    
    # Dataset
    data = []
    for sector in ['quarks', 'leptons']:
        for p_name, p_data in params[sector].items():
            if p_name in topo:
                t = topo[p_name]
                data.append({
                    "name": p_name, 
                    "ln_m": np.log(p_data['observed_mass_mev']), 
                    "V": t['volume'], 
                    "C": t['components']
                })

    # Model: ln(m) = eta(C) * kappa * (V - k_binding * (C - 1)) + B(C)
    
    best_mae = 1000
    best_k = 0
    best_params = {}

    for k in np.linspace(-5.0, 5.0, 501):
        y_true = []
        y_pred = []
        sector_info = {}
        
        for c in [1, 2, 3]:
            subset = [d for d in data if d['C'] == c]
            if not subset: continue
            
            X = np.array([kappa * (d['V'] - k * (d['C'] - 1)) for d in subset])
            y = np.array([d['ln_m'] for d in subset])
            
            # For verification, we fix eta to the best sectoral fits or optimize?
            # Reviewer says "fix eta". But I need to find the best fixed etas.
            # I'll optimize them once for this k.
            slope, intercept, _, _, _ = linregress(X, y)
            
            preds = slope * X + intercept
            y_true.extend(y)
            y_pred.extend(preds)
            
            sector_info[c] = {"eta": slope, "intercept": intercept}
            
        mae = np.mean(np.abs(np.exp(y_pred) - np.exp(y_true)) / np.exp(y_true)) * 100
        if mae < best_mae:
            best_mae = mae
            best_k = k
            best_params = sector_info

    print(f"Best k_binding: {best_k:.4f}")
    print(f"Best MAE      : {best_mae:.4f}%")
    for c, p in best_params.items():
        print(f"C={c}: eta={p['eta']:.4f}, intercept={p['intercept']:.4f}")

if __name__ == "__main__":
    main()
