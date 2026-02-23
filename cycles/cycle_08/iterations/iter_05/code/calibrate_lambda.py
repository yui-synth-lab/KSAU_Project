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
    for q, p in params['quarks'].items():
        t = topo[q]
        data.append({
            "name": q, 
            "ln_m": np.log(p['observed_mass_mev']), 
            "V": t['volume'], 
            "C": t['components'],
            "Det": t['determinant']
        })
    for l, p in params['leptons'].items():
        t = topo[l]
        data.append({
            "name": l, 
            "ln_m": np.log(p['observed_mass_mev']), 
            "V": t['volume'], 
            "C": t['components'],
            "Det": t['determinant']
        })

    # Model: ln(m) = eta(C) * kappa * V + lambda * ln(Det) + B(C)
    # Search for shared 'lambda'
    
    best_mae = 1000
    best_lambda = 0
    best_params = {}

    for lam in np.linspace(-2.0, 2.0, 401):
        y_true = []
        y_pred = []
        sector_info = {}
        
        for c in [1, 2, 3]:
            subset = [d for d in data if d['C'] == c]
            if not subset: continue
            
            # Feature: X = kappa * V, Target = ln(m) - lambda * ln(Det)
            X = np.array([kappa * d['V'] for d in subset])
            y_target = np.array([d['ln_m'] - lam * np.log(d['Det']) for d in subset])
            
            slope, intercept, _, _, _ = linregress(X, y_target)
            
            preds = slope * X + intercept + lam * np.array([np.log(d['Det']) for d in subset])
            y_true.extend([d['ln_m'] for d in subset])
            y_pred.extend(preds)
            
            sector_info[c] = {"eta": slope, "intercept": intercept}
            
        mae = np.mean(np.abs(np.exp(y_pred) - np.exp(y_true)) / np.exp(y_true)) * 100
        if mae < best_mae:
            best_mae = mae
            best_lambda = lam
            best_params = sector_info

    print(f"Best Lambda: {best_lambda:.4f}")
    print(f"Best MAE   : {best_mae:.4f}%")
    for c, p in best_params.items():
        print(f"C={c}: eta={p['eta']:.4f}, intercept={p['intercept']:.4f}")

if __name__ == "__main__":
    main()
