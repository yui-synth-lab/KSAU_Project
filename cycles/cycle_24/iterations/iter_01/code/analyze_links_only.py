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

def analyze_links_only():
    ssot = SSOT()
    _, links_df = ssot.knot_data()
    
    # Prepare Links
    l_df = links_df.copy()
    l_df['u'] = pd.to_numeric(l_df['unlinking_number'], errors='coerce')
    l_df['n'] = pd.to_numeric(l_df['crossing_number'], errors='coerce')
    l_df['det'] = pd.to_numeric(l_df['determinant'], errors='coerce')
    l_df['sig'] = pd.to_numeric(l_df['signature'], errors='coerce')
    l_df['c'] = pd.to_numeric(l_df['components'], errors='coerce')
    
    df = l_df[(l_df['n'] >= 3) & (l_df['n'] <= 12)].copy()
    df = df.dropna(subset=['n', 'det', 'sig', 'c'])
    df['is_resonant'] = (df['det'] % 24 == 0)
    
    # Test F3 (24*c/n) within links
    val_f3 = 24 * df['c'] / df['n']
    med_f3 = val_f3.median()
    is_high = (val_f3 >= med_f3)
    
    a, b, c, d = (
        len(df[(is_high == True) & (df['is_resonant'] == True)]),
        len(df[(is_high == True) & (df['is_resonant'] == False)]),
        len(df[(is_high == False) & (df['is_resonant'] == True)]),
        len(df[(is_high == False) & (df['is_resonant'] == False)])
    )
    or_f3, p_f3 = fisher_exact([[a, b], [c, d]])
    
    # Test F1 (c*|s|/n) within links
    val_f1 = df['c'] * np.abs(df['sig']) / df['n']
    med_f1 = val_f1.median()
    is_high_f1 = (val_f1 >= med_f1)
    
    a1, b1, c1, d1 = (
        len(df[(is_high_f1 == True) & (df['is_resonant'] == True)]),
        len(df[(is_high_f1 == True) & (df['is_resonant'] == False)]),
        len(df[(is_high_f1 == False) & (df['is_resonant'] == True)]),
        len(df[(is_high_f1 == False) & (df['is_resonant'] == False)])
    )
    or_f1, p_f1 = fisher_exact([[a1, b1], [c1, d1]])

    print(f"Within Links Only (N={len(df)}):")
    print(f"F3 (24*c/n): OR={or_f3:.4f}, p={p_f3:.4e}")
    print(f"F1 (c*|s|/n): OR={or_f1:.4f}, p={p_f1:.4e}")

if __name__ == "__main__":
    analyze_links_only()
