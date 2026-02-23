
import sys
import os
import json
from pathlib import Path

import pandas as pd
import numpy as np

# --- Mandatory SSoT Setup ---
SSOT_DIR = Path(r"E:\Obsidian\KSAU_Project\ssot")
sys.path.insert(0, str(SSOT_DIR))
from ksau_ssot import SSOT

def main():
    ssot = SSOT()
    knots_df, _ = ssot.knot_data()
    params = ssot.analysis_params()
    
    knots_df['crossing_number'] = pd.to_numeric(knots_df['crossing_number'], errors='coerce')
    knots_df['volume'] = pd.to_numeric(knots_df['volume'], errors='coerce')
    knots_df['determinant'] = pd.to_numeric(knots_df['determinant'], errors='coerce')
    
    results_by_c = []
    
    for c in range(3, 13):
        df_c = knots_df[(knots_df['crossing_number'] == c) & (knots_df['volume'] > 0)].copy()
        if df_c.empty: continue
        
        alpha_range = np.linspace(0.1, 5.0, 30)
        beta_range = np.linspace(-5.0, 5.0, 31)
        
        best_rate = 0.0
        V = df_c['volume'].values
        Det = df_c['determinant'].values
        
        for a in alpha_range:
            for b in beta_range:
                k_calc = np.floor(a * V + b).astype(int)
                k_calc = np.clip(k_calc, 1, None)
                rate = np.mean(Det % (k_calc + 1) == 0)
                if rate > best_rate:
                    best_rate = rate
                    
        results_by_c.append({
            "crossing_number": int(c),
            "best_rate": float(best_rate),
            "sample_size": len(df_c)
        })
        print(f"C={c}: Best Rate = {best_rate:.4f} (N={len(df_c)})")

    # Output to separate file for analysis
    output_path = Path(__file__).parent.parent / "sector_analysis.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results_by_c, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
