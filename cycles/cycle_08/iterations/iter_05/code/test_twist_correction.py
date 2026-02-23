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
                # twist = (2 - gen) * (-1)**components
                twist = (2 - t['generation']) * ((-1) ** t['components'])
                data.append({
                    "name": p_name, 
                    "ln_m": np.log(p_data['observed_mass_mev']), 
                    "V": t['volume'], 
                    "C": t['components'],
                    "T": twist
                })

    # Fixed best-fit viscosities from Iter 4
    etas = {1: 19.7325, 2: 8.3779, 3: 5.8685}
    
    best_mae = 1000
    best_lam = 0
    best_intercepts = {}

    for lam in np.linspace(-10.0, 10.0, 401):
        y_true, y_pred = [], []
        intercepts = {}
        for c in [1, 2, 3]:
            subset = [d for d in data if d['C'] == c]
            if not subset: continue
            
            # Model: ln(m) = eta * kappa * V + lam * kappa * Twist + B
            target_minus_terms = [d['ln_m'] - etas[c] * kappa * d['V'] - lam * kappa * d['T'] for d in subset]
            B = np.mean(target_minus_terms)
            
            preds = etas[c] * kappa * np.array([d['V'] for d in subset]) + lam * kappa * np.array([d['T'] for d in subset]) + B
            y_true.extend([d['ln_m'] for d in subset])
            y_pred.extend(preds)
            intercepts[c] = B
            
        mae = np.mean(np.abs(np.exp(y_pred) - np.exp(y_true)) / np.exp(y_true)) * 100
        if mae < best_mae:
            best_mae = mae
            best_lam = lam
            best_intercepts = intercepts

    print(f"Best Lambda (Twist): {best_lam:.4f}")
    print(f"Best MAE: {best_mae:.4f}%")
    print(f"Intercepts: {best_intercepts}")

if __name__ == "__main__":
    main()
