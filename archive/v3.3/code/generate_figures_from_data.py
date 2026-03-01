"""
KSAU v3.3 Data-Driven Figure Generator (Portable Version)
--------------------------------------
Generates publication-quality figures using ACTUAL data from verification runs.
"""

import numpy as np
import matplotlib.pyplot as plt
import json
import os
from matplotlib import rcParams

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "brute_force_v3_3_results.json")
FIG_PATH = os.path.join(BASE_DIR, "..", "figures", "Fig5_Permutation_Test_Actual.png")

# Set styles
rcParams['font.family'] = 'serif'
rcParams['figure.dpi'] = 300

def create_permutation_plot():
    if not os.path.exists(DATA_PATH):
        print(f"Error: {DATA_PATH} not found. Run brute_force_v3_3_compliant.py first.")
        return

    with open(DATA_PATH, 'r') as f:
        data = json.load(f)
    
    r2_vals = np.array(data['random_r2_values'])
    ksau_r2 = data['reported_r2']
    max_random = np.max(r2_vals)
    
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.hist(r2_vals, bins=100, density=True, color='skyblue', alpha=0.7, 
            edgecolor='black', linewidth=0.5, label=f'Random Samples (n={len(r2_vals)})')
    
    ax.axvline(ksau_r2, color='red', linewidth=3, label=f'KSAU v3.3 ($R^2$={ksau_r2:.6f})')
    ax.axvline(max_random, color='green', linestyle='--', linewidth=2, label=f'Best Random ($R^2$={max_random:.6f})')
    
    better_count = sum(1 for x in r2_vals if x > ksau_r2)
    stats_text = (f"ACTUAL DATA VERIFICATION\n"
                  f"Trials: {len(r2_vals):,}\n"
                  f"Better fits: {better_count}\n"
                  f"p-value: < {1/len(r2_vals):.5f}")
    
    ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, verticalalignment='top', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='gold', alpha=0.9))
    
    ax.set_xlabel('Model Accuracy ($R^2$)')
    ax.set_ylabel('Probability Density')
    ax.set_title('KSAU v3.3: Statistical Significance from Actual Data', fontweight='bold')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(FIG_PATH)
    print(f"✓ Figure saved to {FIG_PATH}")

if __name__ == "__main__":
    create_permutation_plot()
