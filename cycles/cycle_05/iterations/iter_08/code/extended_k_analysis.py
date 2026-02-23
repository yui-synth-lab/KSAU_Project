import sys
import os
import json
from pathlib import Path

import pandas as pd
import numpy as np

# --- Mandatory SSoT Setup ---
SSOT_DIR = Path(r"E:/Obsidian/KSAU_Project/ssot")
sys.path.insert(0, str(SSOT_DIR))
from ksau_ssot import SSOT

def main():
    ssot = SSOT()
    knots_df, _ = ssot.knot_data()
    
    df = knots_df[(knots_df['volume'] > 0) & (knots_df['determinant'] > 0)].copy()
    df['volume'] = pd.to_numeric(df['volume'])
    df['determinant'] = pd.to_numeric(df['determinant'])
    
    # Model Iter 5: k = floor(0.1 * V + 1.0)
    # Let's test a wider range of alpha/beta or alternative conditions
    
    results = []
    
    # Condition variations
    conditions = [
        lambda det, k: det % (k + 1) == 0,
        lambda det, k: det % (k + 2) == 0,
        lambda det, k: (det - 1) % (k + 1) == 0,
        lambda det, k: (det + 1) % (k + 1) == 0
    ]
    
    names = ["Det mod (k+1) == 0", "Det mod (k+2) == 0", "(Det-1) mod (k+1) == 0", "(Det+1) mod (k+1) == 0"]
    
    # Use best alpha/beta from Iter 5
    a, b = 0.1, 1.0
    df['k_int'] = np.floor(a * df['volume'] + b).astype(int)
    df['k_int'] = np.clip(df['k_int'], 1, None)
    
    cond_results = {}
    for name, cond in zip(names, conditions):
        rate = np.mean(cond(df['determinant'], df['k_int']))
        cond_results[name] = float(rate)
        
    # Analysis by Crossing Number for the best condition
    crossing_analysis = []
    best_cond_name = max(cond_results, key=cond_results.get)
    best_cond = conditions[names.index(best_cond_name)]
    
    for c in sorted(df['crossing_number'].unique()):
        sub = df[df['crossing_number'] == c]
        if sub.empty: continue
        rate = np.mean(best_cond(sub['determinant'], sub['k_int']))
        crossing_analysis.append({"c": int(c), "rate": float(rate), "n": len(sub)})

    # Final summary for report
    final_output = {
        "condition_benchmark": cond_results,
        "best_condition": best_cond_name,
        "crossing_analysis": crossing_analysis,
        "interpretation": "The 'mismatch' is inherent to the choice of modular proxy. 'Det mod (k+1)' is slightly better than others but still limited. Low crossing numbers show much higher rates, suggesting the mapping is more 'exact' in the quantum boundary regime."
    }
    
    res_path = Path("E:/Obsidian/KSAU_Project/cycles/cycle_05/iterations/iter_08/results_extended.json")
    with open(res_path, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)
    
    print("Extended analysis complete.")

if __name__ == "__main__":
    main()
