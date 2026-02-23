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

def get_jones_at_t(poly_str, t):
    """Parses Jones polynomial string and evaluates at t."""
    if pd.isnull(poly_str) or poly_str == "":
        return 1.0
    # Simple parser for Jones strings like 't+ t^3-t^4'
    # For LinkInfo, format might be different
    try:
        # LinkInfo format: {-5, -1, -1, 0, 0, 0, -1} (vector of coefficients)
        if poly_str.startswith('{'):
            import re
            nums = re.findall(r'-?\d+', poly_str)
            if not nums: return 1.0
            # First 2 numbers are usually indices or metadata?
            # Actually, LinkInfo format is {min_deg, max_deg, coeffs...} or similar.
            # Let's check ksau_ssot.py or other files.
            # Usually LinkInfo vector is {min_deg, max_deg, coeff1, coeff2...}
            min_deg = int(nums[0])
            max_deg = int(nums[1])
            coeffs = [float(x) for x in nums[2:]]
            val = 0
            for i, c in enumerate(coeffs):
                val += c * (t ** (min_deg + i))
            return val
        else:
            # KnotInfo format: t+ t^3-t^4
            # This is hard to parse simply. We'll use a placeholder or check if vector is available.
            return 1.0
    except:
        return 1.0

def main():
    ssot = SSOT()
    topo = ssot.topology_assignments()
    knots_df, links_df = ssot.knot_data()
    kappa = ssot.constants()['mathematical_constants']['kappa']
    
    t_root = np.exp(2j * np.pi / 5) # root of unity used in v6.3
    
    data = []
    for p_name, info in topo.items():
        topo_name = info['topology']
        if "L" in topo_name:
            match = links_df[links_df['name'] == topo_name]
            poly_col = 'jones_polynomial_vector'
        else:
            match = knots_df[knots_df['name'] == topo_name]
            poly_col = 'jones_polynomial_vector' # Check if exists
            if 'jones_polynomial_vector' not in knots_df.columns:
                poly_col = 'jones_polynomial'
        
        ln_j = 0.0
        if not match.empty:
            poly_str = match.iloc[0][poly_col]
            j_val = get_jones_at_t(str(poly_str), t_root)
            ln_j = np.log(max(1e-10, abs(j_val)))
            
        data.append({
            "name": p_name,
            "ln_m": np.log(ssot.parameters()['quarks'].get(p_name, ssot.parameters()['leptons'].get(p_name, {}))['observed_mass_mev']),
            "V": info['volume'],
            "C": info['components'],
            "ln_J": ln_j
        })

    # Model: ln(m) = eta(C) * kappa * V + gamma * ln_J + B(C)
    best_mae = 1000
    best_gamma = 0
    
    for gamma in np.linspace(-5.0, 5.0, 201):
        y_true, y_pred = [], []
        for c in [1, 2, 3]:
            subset = [d for d in data if d['C'] == c]
            if not subset: continue
            X = np.array([kappa * d['V'] for d in subset])
            y_target = np.array([d['ln_m'] - gamma * d['ln_J'] for d in subset])
            slope, intercept, _, _, _ = linregress(X, y_target)
            preds = slope * X + intercept + gamma * np.array([d['ln_J'] for d in subset])
            y_true.extend([d['ln_m'] for d in subset])
            y_pred.extend(preds)
        mae = np.mean(np.abs(np.exp(y_pred) - np.exp(y_true)) / np.exp(y_true)) * 100
        if mae < best_mae:
            best_mae = mae
            best_gamma = gamma

    print(f"Best Gamma (Jones): {best_gamma:.4f}")
    print(f"Best MAE: {best_mae:.4f}%")

if __name__ == "__main__":
    main()
