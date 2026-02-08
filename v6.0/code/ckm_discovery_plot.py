import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import ksau_config
from pathlib import Path

def discover_ckm_geometry():
    # 1. Load Data
    try:
        data = ksau_config.load_topology_assignments()
        phys = ksau_config.load_physical_constants()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    # 2. Map Quarks to Volumes
    vols = {name: info['volume'] for name, info in data.items() if info['charge_type'] != 'lepton'}
    
    # 3. Experimental CKM Magnitudes
    ckm_matrix = np.array(phys['ckm']['matrix'])
    
    up_type = ['Up', 'Charm', 'Top']
    down_type = ['Down', 'Strange', 'Bottom']
    
    deltas = []
    log_v = []
    labels = []
    
    for i, u in enumerate(up_type):
        for j, d in enumerate(down_type):
            dv = abs(vols[u] - vols[d])
            mag = ckm_matrix[i, j]
            
            deltas.append(dv)
            log_v.append(np.log(mag))
            labels.append(f"{u[0]}{d[0]}")

    # 4. Statistical Discovery
    slope, intercept, r_value, p_value, std_err = stats.linregress(deltas, log_v)
    
    print("="*80)
    print("KSAU DISCOVERY: CKM Mixing vs Topological Proximity")
    print("="*80)
    print(f"Volume-Mixing Correlation R: {r_value:.4f}")
    print(f"P-value: {p_value:.2e} (Significance)")
    print(f"Derived Law: |V_ij| = {np.exp(intercept):.2f} * exp({slope:.3f} * dVol)")
    print("-" * 80)
    
    # Cabibbo Angle Point
    dv_us = abs(vols['Up'] - vols['Strange'])
    print(f"Focus: V_us (Cabibbo Angle)")
    print(f"  Delta Vol (Up-Strange) : {dv_us:.4f}")
    print(f"  Experimental |V_us|    : 0.2253")
    print(f"  Predicted exp(-0.5*dV) : {np.exp(-0.5 * dv_us):.4f}")
    print(f"  Error: {abs(np.exp(-0.5 * dv_us) - 0.2253)/0.2253:.2%}")
    print("-" * 80)

    # 6. Visualization
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(deltas, log_v, s=200, c='gold', edgecolors='black', alpha=0.8, label='CKM Elements')
    
    x_fit = np.linspace(0, max(deltas), 100)
    ax.plot(x_fit, slope * x_fit + intercept, 'r--', label=f'Geometric Fit (R={r_value:.2f})')
    ax.plot(x_fit, -0.5 * x_fit, 'b:', alpha=0.5, label='Theoretical Baseline (k=0.5)')
    
    for i, txt in enumerate(labels):
        ax.annotate(txt, (deltas[i], log_v[i]), xytext=(7, 7), textcoords='offset points', fontsize=12, fontweight='bold')

    ax.set_xlabel(r'Topological Volume Difference ($\Delta V$)', fontsize=14)
    ax.set_ylabel(r'Log Mixing Amplitude ($\ln |V_{ij}| $)', fontsize=14)
    ax.set_title('The Geometric Origin of Flavor Mixing', fontsize=16)
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Simplified text to avoid LaTeX errors
    ax.text(0.5, 0.1, "ln |V_ij| ~ -0.5 * Delta V", transform=ax.transAxes, 
            fontsize=15, color='blue', bbox=dict(facecolor='white', alpha=0.8))

    output_dir = Path('v6.0/figures')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'ckm_discovery_plot.png', dpi=300)
    print("Discovery plot saved to v6.0/figures/ckm_discovery_plot.png")
    print("="*80)

if __name__ == "__main__":
    discover_ckm_geometry()
