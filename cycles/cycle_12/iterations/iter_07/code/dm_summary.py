
import sys
import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
import time

# --- Dynamic SSoT Setup ---
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
sys.path.insert(0, str(project_root / "ssot"))
from ksau_ssot import SSOT

def main():
    start_time = time.time()
    ssot = SSOT()
    consts = ssot.constants()
    knots_df, _ = ssot.knot_data()
    
    # 1. Top 3 Candidates
    top_3_names = ['12a_435', '12a_462', '12a_125']
    
    # 2. Prediction Parameters
    # Using Unified Mass Law from Architecture Note: ln(m) = kappa * V + c
    # kappa = pi/24
    math_consts = consts.get("mathematical_constants", {})
    kappa = math_consts.get("kappa", 0.13089969)
    # Intercept from v6.1 dark_matter_scan.py: intercept = -(7.0 + G_catalan)
    G_catalan = math_consts.get("G_catalan", 0.91596559)
    intercept = -(7.0 + G_catalan)
    # Slope for bulk (quarks/DM) from v6.1: slope = (10/7 * G_catalan)
    slope = (10.0 / 7.0) * G_catalan
    
    subset = knots_df[knots_df['name'].isin(top_3_names)].copy()
    
    final_summary = []
    for _, row in subset.iterrows():
        name = row['name']
        vol = float(row.get('volume', 0))
        det = int(row.get('determinant', 0))
        
        # Mass Prediction
        ln_m = slope * vol + intercept
        mass_mev = np.exp(ln_m)
        
        # Stability (TSI)
        # Formula: n + u + |s|
        n = int(row.get('crossing_number', 12))
        # Note: unknotting number can be list-like string in CSV sometimes, but here we assume numeric for simplicity
        # Wait, I should parse it correctly.
        try:
            u_str = str(row.get('unknotting_number', '0'))
            # check for list like [1] or 1
            if '[' in u_str:
                import re
                nums = re.findall(r'\d+', u_str)
                u = int(nums[0]) if nums else 0
            else:
                u = int(float(u_str))
        except:
            u = 0
            
        s = int(row.get('signature', 0))
        tsi = n + u + abs(s)
        
        final_summary.append({
            "name": name,
            "symmetry": row['symmetry_type'],
            "predicted_mass_gev": mass_mev / 1000.0,
            "determinant": det,
            "tsi_stability": tsi,
            "interaction_protection": "maximal (fully amphicheiral)" if "fully" in str(row['symmetry_type']).lower() else "high (amphicheiral)"
        })

    # 3. Output results
    # Read existing results.json to add this summary
    output_path = current_file.parents[1] / "results.json"
    with open(output_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    data["computed_values"]["final_summary"] = final_summary
    data["task_name"] += " および 物理的特性のまとめ"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print("Final summary added to results.json.")

if __name__ == "__main__":
    main()
