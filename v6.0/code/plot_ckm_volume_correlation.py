
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import scipy.stats as stats

def plot_ckm_volume_correlation():
    # ---------------------------------------------------------
    # 1. Setup Data
    # ---------------------------------------------------------
    csv_path = Path('data/linkinfo_data_complete.csv')
    if not csv_path.exists():
        print("Error: CSV not found.")
        return

    df = pd.read_csv(csv_path, sep='|', skiprows=[1])
    
    # Assignments
    assignments = {
        'u': 'L8a6{0}', 'c': 'L11n64{0}', 't': 'L11a62{0}',
        'd': 'L6a4{0,0}', 's': 'L10n95{0,0}', 'b': 'L10a140{0,0}'
    }
    
    vols = {}
    for k, v in assignments.items():
        row = df[df['name'] == v].iloc[0]
        vols[k] = float(row['volume'])

    # CKM Magnitude (PDG 2022)
    ckm_exp = {
        ('u','d'): 0.9743, ('u','s'): 0.2253, ('u','b'): 0.0036,
        ('c','d'): 0.2252, ('c','s'): 0.9734, ('c','b'): 0.0410,
        ('t','d'): 0.0086, ('t','s'): 0.0405, ('t','b'): 0.9991
    }
    
    # ---------------------------------------------------------
    # 2. Process Correlation
    # ---------------------------------------------------------
    deltas = []
    log_v = []
    labels = []
    colors = []
    
    # Categorize transitions
    # Diagonal (u-d, c-s, t-b): Dominant
    # Off-diagonal: Suppressed
    
    for (u, d), val in ckm_exp.items():
        d_vol = abs(vols[u] - vols[d])
        ln_val = np.log(val)
        
        deltas.append(d_vol)
        log_v.append(ln_val)
        labels.append(f"{u}{d}")
        
        if val > 0.5:
            colors.append('red') # Diagonal-ish
        else:
            colors.append('blue') # Off-diagonal

    # Linear Regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(deltas, log_v)
    
    print("="*80)
    print("KSAU v6.0: CKM Mixing vs Topological Volume Difference")
    print("="*80)
    print(f"Correlation Coefficient R : {r_value:.4f}")
    print(f"R-squared                 : {r_value**2:.4f}")
    print(f"Slope (Decay Constant k)  : {slope:.4f}")
    print(f"Intercept                 : {intercept:.4f}")
    print("-" * 80)
    print("Hypothesis Check:")
    print("If |V_ij| ~ exp(-k * dVol), we expect a clean linear fit.")
    print(f"Result: |V_ij| ~ exp({slope:.2f} * dVol)")
    print("Compare with previous manual check: k ~ 0.5 for V_us.")
    
    # ---------------------------------------------------------
    # 3. Visualization
    # ---------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.scatter(deltas, log_v, c=colors, s=100, edgecolors='black', zorder=5)
    
    # Regression Line
    x_range = np.linspace(min(deltas), max(deltas), 100)
    y_range = slope * x_range + intercept
    ax.plot(x_range, y_range, 'k--', alpha=0.5, label=f'Fit: k={abs(slope):.2f}')
    
    # Annotate points
    for i, txt in enumerate(labels):
        ax.annotate(txt, (deltas[i], log_v[i]), xytext=(5, 5), textcoords='offset points')
        
    ax.set_xlabel('Topological Volume Difference ($\Delta V$)')
    ax.set_ylabel('Log Mixing Magnitude ($\ln |V_{ij}|$)')
    ax.set_title('CKM Matrix: The Geometry of Flavor Mixing')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.3)
    
    # Theoretical Line k=0.5 (kappa dependent?)
    # kappa = pi/24 ~ 0.13. 
    # k=0.5 corresponds to ~ 4 * kappa.
    y_theory = -0.5 * x_range
    ax.plot(x_range, y_theory, 'r:', alpha=0.5, label='Theory: -0.5 * dVol')
    ax.legend()

    output_path = 'v6.0/figures/ckm_volume_correlation.png'
    plt.savefig(output_path, dpi=300)
    print(f"Plot saved to {output_path}")
    print("="*80)

if __name__ == "__main__":
    plot_ckm_volume_correlation()
