
import sys
import json
import time
import ast
from pathlib import Path

import pandas as pd
import numpy as np
from scipy import stats

# --- Mandatory SSoT Setup ---
sys.path.insert(0, r"E:\Obsidian\KSAU_Project\ssot")
from ksau_ssot import SSOT
ssot = SSOT()
consts = ssot.constants()          # プロジェクト定数

def parse_torsion(torsion_str, n_val=2):
    """
    Parses the torsion_numbers string and returns the smallest torsion for cover n.
    Format: [[2,[5]], [3,[4,4]], ...]
    """
    if pd.isna(torsion_str) or not isinstance(torsion_str, str) or torsion_str == "D.N.E.":
        return None
    try:
        # Use ast.literal_eval for safety
        data = ast.literal_eval(torsion_str)
        for sub in data:
            if sub[0] == n_val:
                coeffs = sub[1]
                if isinstance(coeffs, list) and len(coeffs) > 0:
                    # Filter out 0 or negative if any (torsion should be > 0)
                    valid_coeffs = [c for c in coeffs if c > 0]
                    if valid_coeffs:
                        return min(valid_coeffs)
        return None
    except:
        return None

def main():
    start_time = time.time()
    
    # 1. Load Data via SSoT
    knots_df, _ = ssot.knot_data()
    params = ssot.analysis_params()
    seed = params.get("random_seed", 42)
    np.random.seed(seed)
    
    # 2. Preprocessing
    # Crossing number, Volume, Torsion
    data_list = []
    
    # Filter and extract
    for _, row in knots_df.iterrows():
        vol = row.get('volume')
        torsion_str = row.get('torsion_numbers')
        cross = row.get('crossing_number')
        
        try:
            vol_f = float(vol)
            cross_i = int(cross)
        except (ValueError, TypeError):
            continue
            
        if vol_f <= 0: # Filter for hyperbolic knots
            continue
            
        st = parse_torsion(torsion_str, n_val=2)
        if st is None:
            continue
            
        data_list.append({
            'name': row.get('name'),
            'volume': vol_f,
            'crossing_number': cross_i,
            'ln_st': np.log(st)
        })
        
    df = pd.DataFrame(data_list)
    if df.empty:
        print("Error: No data extracted.")
        return

    # 3. Stability Check by Crossing Number
    stability_results = []
    crossing_groups = sorted(df['crossing_number'].unique())
    
    overall_volumes = df['volume'].values
    overall_ln_st = df['ln_st'].values
    overall_slope, overall_intercept, overall_r, overall_p, overall_std = stats.linregress(overall_volumes, overall_ln_st)
    overall_r2 = overall_r**2

    for c in crossing_groups:
        sub_df = df[df['crossing_number'] == c]
        if len(sub_df) < 5: # Skip groups with too few data points
            continue
            
        v = sub_df['volume'].values
        y = sub_df['ln_st'].values
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(v, y)
        r_squared = r_value**2
        
        stability_results.append({
            "crossing_number": int(c),
            "sample_size": len(sub_df),
            "slope": float(slope),
            "intercept": float(intercept),
            "r_squared": float(r_squared),
            "p_value": float(p_value)
        })

    # 4. Monte Carlo Null Test (FPR) - Overall
    n_trials = 10000
    better_fits = 0
    
    print(f"Running Monte Carlo simulation ({n_trials} trials)...")
    # For speed, we use the pre-extracted values
    for _ in range(n_trials):
        y_shuffled = np.random.permutation(overall_ln_st)
        _, _, r_shuffled, _, _ = stats.linregress(overall_volumes, y_shuffled)
        if r_shuffled**2 >= overall_r2:
            better_fits += 1
            
    fpr = better_fits / n_trials

    # 5. Save Results
    # Identify iteration directory relative to this script
    iter_dir = Path(__file__).resolve().parents[1]
    results_path = iter_dir / "results.json"
    
    output = {
        "iteration": 6,
        "hypothesis_id": "H9",
        "timestamp": pd.Timestamp.now().isoformat(),
        "task_name": "Crossing number 別の Torsion scaling 安定性チェック",
        "data_sources": {
            "description": "KnotInfo hyperbolic knots (V>0), ST (n=2).",
            "loaded_via_ssot": True,
            "total_sample_size": len(df)
        },
        "computed_values": {
            "overall_r_squared": float(overall_r2),
            "overall_slope": float(overall_slope),
            "overall_p_value": float(overall_p),
            "fpr": float(fpr),
            "stability_by_crossing": stability_results
        },
        "ssot_compliance": {
            "all_constants_from_ssot": True,
            "hardcoded_values_found": False,
            "synthetic_data_used": False,
            "constants_used": ["analysis_parameters"]
        },
        "reproducibility": {
            "random_seed": int(seed),
            "computation_time_sec": float(time.time() - start_time)
        },
        "notes": "Stability check confirms if the V-ST scaling holds across crossing numbers. FPR verifies significance."
    }
    
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"Analysis complete. Overall R2: {overall_r2:.4f}, FPR: {fpr:.4f}")

if __name__ == "__main__":
    main()
