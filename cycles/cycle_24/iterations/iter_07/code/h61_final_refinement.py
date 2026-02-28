import sys
from pathlib import Path
import pandas as pd
import numpy as np
from scipy.stats import fisher_exact
import json

# SSoT Loading
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
ssot_path = project_root / "ssot"
sys.path.insert(0, str(ssot_path))    
from ksau_ssot import SSOT

def main():
    ssot = SSOT()
    consts = ssot.constants()
    k_resonance = consts['mathematical_constants']['k_resonance']
    knots_df, links_df = ssot.knot_data()
    
    # 1. Combined Data Analysis
    # Prepare Knots
    k_df = knots_df.copy()
    k_df['n'] = pd.to_numeric(k_df['crossing_number'], errors='coerce')
    k_df['det'] = pd.to_numeric(k_df['determinant'], errors='coerce')
    k_df['sig'] = pd.to_numeric(k_df['signature'], errors='coerce')
    k_df['c'] = 1
    
    # Prepare Links
    l_df = links_df.copy()
    l_df['n'] = pd.to_numeric(l_df['crossing_number'], errors='coerce')
    l_df['det'] = pd.to_numeric(l_df['determinant'], errors='coerce')
    l_df['sig'] = pd.to_numeric(l_df['signature'], errors='coerce')
    l_df['c'] = pd.to_numeric(l_df['components'], errors='coerce')
    
    # Combine
    all_df = pd.concat([
        k_df[['n', 'det', 'sig', 'c']],
        l_df[['n', 'det', 'sig', 'c']]
    ], ignore_index=True)
    
    all_df = all_df[(all_df['n'] >= 3) & (all_df['n'] <= 12)].copy()
    all_df = all_df.dropna(subset=['n', 'det', 'sig', 'c'])
    all_df['is_resonant'] = (all_df['det'] % k_resonance == 0)
    
    # Refined Formula: TSI_24 = 24 * c / (n + |s|)
    def tsi_refined(d):
        return k_resonance * d['c'] / (d['n'] + np.abs(d['sig']))

    all_df['tsi'] = tsi_refined(all_df)
    med = all_df['tsi'].median()
    high = (all_df['tsi'] >= med)
    
    a, b, c, d = (
        len(all_df[(high == True) & (all_df['is_resonant'] == True)]),
        len(all_df[(high == True) & (all_df['is_resonant'] == False)]),
        len(all_df[(high == False) & (all_df['is_resonant'] == True)]),
        len(all_df[(high == False) & (all_df['is_resonant'] == False)])
    )
    or_all, p_all = fisher_exact([[a, b], [c, d]])
    
    # 2. Links-Only Analysis (Internal validation)
    links_only = all_df[all_df['c'] >= 2].copy()
    med_l = links_only['tsi'].median()
    high_l = (links_only['tsi'] >= med_l)
    
    la, lb, lc, ld = (
        len(links_only[(high_l == True) & (links_only['is_resonant'] == True)]),
        len(links_only[(high_l == True) & (links_only['is_resonant'] == False)]),
        len(links_only[(high_l == False) & (links_only['is_resonant'] == True)]),
        len(links_only[(high_l == False) & (links_only['is_resonant'] == False)])
    )
    or_link, p_link = fisher_exact([[la, lb], [lc, ld]])

    # 3. Output results
    results = {
        "iteration": 7,
        "hypothesis_id": "H61",
        "timestamp": pd.Timestamp.now().isoformat(),
        "task_name": "不一致領域の幾何学的要因分析と公式の微調整",
        "refined_formula": "24 * c / (n + |s|)",
        "combined_stats": {
            "n": len(all_df),
            "odds_ratio": float(or_all),
            "p_value": float(p_all),
            "table": {"tp": a, "fp": b, "fn": c, "tn": d}
        },
        "links_only_stats": {
            "n": len(links_only),
            "odds_ratio": float(or_link),
            "p_value": float(p_link),
            "table": {"tp": la, "fp": lb, "fn": lc, "tn": ld}
        },
        "ssot_compliance": {"all_constants_from_ssot": True},
        "reproducibility": {"random_seed": 42}
    }
    
    with open(project_root / "cycles/cycle_24/iterations/iter_07/results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
