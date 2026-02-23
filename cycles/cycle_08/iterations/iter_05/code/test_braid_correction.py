import numpy as np
import sys
import json
import pandas as pd
from pathlib import Path
from scipy.stats import linregress
from sklearn.metrics import r2_score

# SSoT Loader setup
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
ssot_dir = project_root / "ssot"
sys.path.insert(0, str(ssot_dir))
from ksau_ssot import SSOT

def parse_braid(val):
    if pd.isnull(val): return 2.0
    s = str(val).strip()
    if s == "" or s == "undefined": return 2.0
    import re
    nums = re.findall(r'-?\d+', s)
    if nums: return float(nums[0])
    return 2.0

def main():
    ssot = SSOT()
    topo = ssot.topology_assignments()
    knots_df, links_df = ssot.knot_data()
    kappa = ssot.constants()['mathematical_constants']['kappa']
    params = ssot.parameters()
    
    data = []
    for p_name, info in topo.items():
        topo_name = info['topology']
        if "L" in topo_name:
            match = links_df[links_df['name'] == topo_name]
        else:
            match = knots_df[knots_df['name'] == topo_name]
        
        b_idx = 2.0
        if not match.empty:
            b_idx = parse_braid(match.iloc[0]['braid_index'])
            
        p_data = params['quarks'].get(p_name) or params['leptons'].get(p_name)
        if not p_data: continue
            
        data.append({
            "name": p_name,
            "ln_m": np.log(p_data['observed_mass_mev']),
            "V": info['volume'],
            "C": info['components'],
            "B": b_idx
        })

    # Model: ln(m) = eta(C) * kappa * (V - delta * B) + Intercept
    best_mae = 1000
    best_delta = 0
    best_params = {}

    for delta in np.linspace(-2.0, 2.0, 401):
        y_true, y_pred = [], []
        sector_info = {}
        for c in [1, 2, 3]:
            subset = [d for d in data if d['C'] == c]
            if len(subset) < 2: continue
            X = np.array([kappa * (d['V'] - delta * d['B']) for d in subset])
            y = np.array([d['ln_m'] for d in subset])
            slope, intercept, _, _, _ = linregress(X, y)
            preds = slope * X + intercept
            y_true.extend(y)
            y_pred.extend(preds)
            sector_info[c] = {"eta": slope, "intercept": intercept}
        mae = np.mean(np.abs(np.exp(y_pred) - np.exp(y_true)) / np.exp(y_true)) * 100
        if mae < best_mae:
            best_mae = mae
            best_delta = delta
            best_params = sector_info

    print(f"Best Delta (Braid): {best_delta:.4f}")
    print(f"Best MAE: {best_mae:.4f}%")
    for c, p in best_params.items():
        print(f"C={c}: eta={p['eta']:.4f}, intercept={p['intercept']:.4f}")

if __name__ == "__main__":
    main()
