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

    # Model: ln(m) = eta(C) * kappa * (V - delta * ln(Det)) + B(C)
    # We'll search for 'delta' that minimizes overall MAE when eta(C) and B(C) are optimized.
    
    best_overall_mae = 1000
    best_delta = 0
    best_params = {}

    for delta in np.linspace(-1.0, 1.0, 201):
        y_true = []
        y_pred = []
        sector_info = {}
        
        for c in [1, 2, 3]:
            subset = [d for d in data if d['C'] == c]
            if not subset: continue
            
            # Feature: V_eff = V - delta * ln(Det)
            X = np.array([d['V'] - delta * np.log(d['Det']) for d in subset])
            y = np.array([d['ln_m'] for d in subset])
            
            if len(subset) >= 2:
                slope, intercept, r_val, p_val, _ = linregress(X, y)
            else:
                # For C=1, we have 3 points. For C=2, 3 points. For C=3, 3 points. All have >= 2.
                continue
                
            preds = slope * X + intercept
            y_true.extend(y)
            y_pred.extend(preds)
            
            sector_info[c] = {"slope": slope, "intercept": intercept, "eta": slope/kappa}
            
        mae = np.mean(np.abs(np.exp(y_pred) - np.exp(y_true)) / np.exp(y_true)) * 100
        if mae < best_overall_mae:
            best_overall_mae = mae
            best_delta = delta
            best_params = sector_info

    print(f"Best Delta: {best_delta:.4f}")
    print(f"Best MAE  : {best_overall_mae:.4f}%")
    
    for c, p in best_params.items():
        print(f"C={c}: eta={p['eta']:.4f}, intercept={p['intercept']:.4f}")

    # Re-calculate R2
    y_true = []
    y_pred = []
    for d in data:
        p = best_params[d['C']]
        v_eff = d['V'] - best_delta * np.log(d['Det'])
        ln_m_pred = p['slope'] * v_eff + p['intercept']
        y_true.append(d['ln_m'])
        y_pred.append(ln_m_pred)
    
    r2 = r2_score(y_true, y_pred)
    print(f"Total R2: {r2:.6f}")

if __name__ == "__main__":
    main()
