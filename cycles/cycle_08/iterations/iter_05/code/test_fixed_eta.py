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
    
    data = []
    for sector in ['quarks', 'leptons']:
        for p_name, p_data in params[sector].items():
            if p_name in topo:
                t = topo[p_name]
                data.append({
                    "name": p_name, 
                    "ln_m": np.log(p_data['observed_mass_mev']), 
                    "V": t['volume'], 
                    "C": t['components'],
                    "N": t['crossing_number']
                })

    # Fixed Theoretical Viscosities
    etas = {1: 20.0, 2: 10.0, 3: 6.6667}
    
    best_mae = 1000
    best_gamma = 0
    best_intercepts = {}

    for gamma in np.linspace(-1.0, 1.0, 201):
        y_true, y_pred = [], []
        intercepts = {}
        for c in [1, 2, 3]:
            subset = [d for d in data if d['C'] == c]
            if not subset: continue
            
            # Prediction with fixed eta: ln(m) = eta * kappa * (V - gamma * N) + B
            # Find B that minimizes MAE for this sector
            target_minus_slope = [d['ln_m'] - etas[c] * kappa * (d['V'] - gamma * d['N']) for d in subset]
            B = np.mean(target_minus_slope) # Intercept
            
            preds = etas[c] * kappa * (np.array([d['V'] - gamma * d['N'] for d in subset])) + B
            y_true.extend([d['ln_m'] for d in subset])
            y_pred.extend(preds)
            intercepts[c] = B
            
        mae = np.mean(np.abs(np.exp(y_pred) - np.exp(y_true)) / np.exp(y_true)) * 100
        if mae < best_mae:
            best_mae = mae
            best_gamma = gamma
            best_intercepts = intercepts

    print(f"Best Gamma: {best_gamma:.4f}")
    print(f"Best MAE  : {best_mae:.4f}%")
    print(f"Intercepts: {best_intercepts}")

if __name__ == "__main__":
    main()
