import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import os
import ksau_config

def analyze_g2_data_driven():
    # 1. Load physical constants from config
    phys = ksau_config.load_physical_constants()
    ALPHA_GEOM = ksau_config.ALPHA_GEOM
    A_BASE = 1.0 / 864.0

    csv_knot = ksau_config.load_knotinfo_path()
    df_k = pd.read_csv(csv_knot, sep='|', skiprows=[1])

    def get_vol(name):
        row = df_k[df_k['name'] == name].iloc[0]
        v = row['volume']
        return float(v) if v != 'Not Hyperbolic' else 0.0

    leptons = {
        'Electron': {'a_exp': phys['g_minus_2']['a_e_exp'], 'name': '3_1'},
        'Muon':     {'a_exp': phys['g_minus_2']['a_mu_exp'],  'name': '6_1'},
        'Tau':      {'a_exp': 0.00117721,     'name': '7_1'}  # Tau g-2 not in database yet
    }
    
    for k in leptons:
        leptons[k]['Vol'] = get_vol(leptons[k]['name'])

    print("="*80)
    print("KSAU v6.0 Data-Driven: g-2 Analysis")
    print("="*80)
    print(f"Base Anomaly (1/864): {A_BASE:.9f}")
    print("-" * 80)
    
    for name, data in leptons.items():
        diff = data['a_exp'] - A_BASE
        print(f"{name:<10} | Exp: {data['a_exp']:.9f} | Diff: {diff:+.9f} | Vol: {data['Vol']:.4f}")
    
    # Muon Excess
    delta_mu_e = leptons['Muon']['a_exp'] - leptons['Electron']['a_exp']
    vol_mu = leptons['Muon']['Vol']
    term_try = (ALPHA_GEOM / (2*np.pi))**2 * vol_mu
    
    print("-" * 80)
    print(f"Muon Excess (a_mu - a_e)     : {delta_mu_e:.9e}")
    print(f"Theory (alpha/2pi)^2 * Vol   : {term_try:.9e}")
    print(f"Ratio (Exp / Theory)         : {delta_mu_e / term_try:.4f}")
    print("="*80)

    # Visualization
    fig, ax = plt.subplots(figsize=(8, 5))
    x_vals = [0, 1]
    y_vals = [leptons['Electron']['a_exp'], leptons['Muon']['a_exp']]
    ax.scatter(x_vals, y_vals, s=100, color=['blue', 'red'], label='Experimental')
    ax.axhline(A_BASE, color='green', linestyle='--', label='Geometric Base (1/864)')
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['Electron', 'Muon'])
    ax.set_ylabel('g-2 Anomaly (a)')
    ax.set_title('Topological g-2: Data-Driven Analysis')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.savefig('v6.0/figures/g_minus_2_analysis.png')
    print("Plot saved to v6.0/figures/g_minus_2_analysis.png")

if __name__ == "__main__":
    analyze_g2_data_driven()