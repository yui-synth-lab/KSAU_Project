import numpy as np
import sys
import json
import pandas as pd
from pathlib import Path
from scipy.stats import linregress

# SSoT Loader setup
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
ssot_dir = project_root / "ssot"
sys.path.insert(0, str(ssot_dir))
from ksau_ssot import SSOT

def parse_val(val, default=0.0):
    if pd.isnull(val): return default
    s = str(val).strip()
    if s == "" or s == "undefined" or s == "Not Hyperbolic": return default
    import re
    nums = re.findall(r'-?\d+', s)
    if nums: return float(nums[0])
    return default

def main():
    ssot = SSOT()
    topo = ssot.topology_assignments()
    knots_df, links_df = ssot.knot_data()
    params = ssot.parameters()
    kappa = ssot.constants()['mathematical_constants']['kappa']
    
    alpha, beta = 0.1, 0.1
    
    data = []
    for sector_name in ['quarks', 'leptons', 'bosons']:
        for p_name, p_data in params[sector_name].items():
            if p_name not in topo: continue
            info = topo[p_name]
            topo_name = info['topology']
            if "L" in topo_name: match = links_df[links_df['name'] == topo_name]
            else: match = knots_df[knots_df['name'] == topo_name]
            sig = parse_val(match.iloc[0]['signature']) if not match.empty else 0.0
            twist = (2 - info.get('generation', 2)) * ((-1) ** info['components'])
            mass = p_data.get('observed_mass_mev') or p_data.get('observed_mass')
            if not mass: continue
            data.append({"name": p_name, "ln_m": np.log(mass), "V": info['volume'], "C": info['components'], "S": sig, "T": twist, "sector": sector_name})

    print("--- Final Calibrated Model Parameters ---")
    final_params = {}
    for s in ["quarks", "leptons", "bosons"]:
        subset = [d for d in data if d['sector'] == s]
        if s == "quarks":
            for c in [2, 3]:
                c_subset = [d for d in subset if d['C'] == c]
                X = np.array([d['V'] + alpha * d['T'] + beta * d['S'] for d in c_subset])
                y = np.array([d['ln_m'] for d in c_subset])
                slope, intercept, _, _, _ = linregress(X, y)
                final_params[f"Quark_C{c}"] = {"eta": slope/kappa, "intercept": intercept}
        else:
            X = np.array([d['V'] + alpha * d['T'] + beta * d['S'] for d in subset])
            y = np.array([d['ln_m'] for d in subset])
            slope, intercept, _, _, _ = linregress(X, y)
            final_params[s] = {"eta": slope/kappa, "intercept": intercept}
            
    print(json.dumps(final_params, indent=2))

if __name__ == "__main__":
    main()
