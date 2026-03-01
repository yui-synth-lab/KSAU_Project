import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
import ksau_config
from pathlib import Path

def predict_top_spin_data_driven():
    # 1. Constants
    KAPPA = np.pi / 24
    
    # Load official Top quark topology
    topo = ksau_config.load_topology_assignments()
    top_info = topo['Top']
    top_name = top_info['topology']
    
    # Load linkinfo data
    csv_path = Path('data/linkinfo_data_complete.csv')
    df = pd.read_csv(csv_path, sep='|', skiprows=[1])
    
    # Extract row
    base_name = top_name.split('{')[0]
    row = df[df['name'].str.startswith(base_name)].iloc[0]
    
    vol_top = float(row['volume'])
    comp_top = int(row['components'])
    
    # 2. SM Values (Load from config)
    phys = ksau_config.load_physical_constants()
    sm = phys['top_helicity_sm']
    F0_SM = sm['F0']
    FL_SM = sm['FL']
    FR_SM = sm['FR']
    ERR_SM = sm['error_sm'] 

    # 3. KSAU Prediction
    # Twist calculation: (2 - Gen) * (-1)^Comp
    gen_top = top_info['generation']
    
    twist = (2 - gen_top) * ((-1)**comp_top)
    twist_magnitude = abs(twist)
    
    # KSAU Prediction: Anomaly ~ alpha_geom / 10
    ALPHA_GEOM = ksau_config.ALPHA_GEOM
    delta_FR = (ALPHA_GEOM / 10) * twist_magnitude
    
    FR_KSAU = FR_SM + delta_FR
    norm = (F0_SM + FL_SM)
    F0_KSAU = F0_SM - (delta_FR * (F0_SM / norm))
    FL_KSAU = FL_SM - (delta_FR * (FL_SM / norm))
    
    print("="*70)
    print("KSAU v6.0 Data-Driven: Top Quark Helicity Prediction")
    print("="*70)
    print(f"Top Link                 : {row['name']}")
    print(f"Hyperbolic Volume (Data) : {vol_top:.5f}")
    print(f"Components (Data)        : {comp_top}")
    print(f"Calculated Twist         : {twist}")
    print(f"Predicted Anomaly        : +{delta_FR:.5f} (alpha_geom/10)")
    print("-"*70)
    print(f"{'Helicity':<10} | {'SM Prediction':<15} | {'KSAU Prediction':<15} | {'Deviation':<10}")
    print("-"*70)
    print(f"{'F_0':<10} | {F0_SM:.4f}          | {F0_KSAU:.4f}          | {F0_KSAU-F0_SM:+.4f}")
    print(f"{'F_L':<10} | {FL_SM:.4f}          | {FL_KSAU:.4f}          | {FL_KSAU-FL_SM:+.4f}")
    print(f"{'F_R':<10} | {FR_SM:.4f}          | {FR_KSAU:.4f}          | {FR_KSAU-FR_SM:+.4f}")
    print("="*70)

    # 4. Visualization
    fractions = ['F_0', 'F_L', 'F_R']
    sm_vals = [F0_SM, FL_SM, FR_SM]
    ksau_vals = [F0_KSAU, FL_KSAU, FR_KSAU]
    
    x = np.arange(len(fractions))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(x - width/2, sm_vals, width, label='Standard Model', color='gray', alpha=0.7, yerr=ERR_SM, capsize=5)
    ax.bar(x + width/2, ksau_vals, width, label='KSAU v6.0', color='#FF6666', alpha=0.9, yerr=ERR_SM, capsize=5)

    ax.set_ylabel('Helicity Fraction')
    ax.set_title('Top Quark Decay Helicity: Data-Driven Prediction')
    ax.set_xticks(x)
    ax.set_xticklabels(fractions)
    ax.legend()
    
    ax.annotate(f'Anomaly\n+{delta_FR:.1%}',
                xy=(2 + width/2, FR_KSAU),
                xytext=(2 + width/2, FR_KSAU + 0.15),
                arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=8),
                ha='center', fontsize=12, color='red', fontweight='bold')

    ax.set_ylim(0, 0.9)
    ax.grid(True, axis='y', linestyle='--', alpha=0.3)
    
    plt.tight_layout()
    output_path = os.path.join('v6.0', 'figures', 'top_spin_correlation.png')
    plt.savefig(output_path, dpi=300)
    print(f"Plot saved to {output_path}")

if __name__ == "__main__":
    predict_top_spin_data_driven()