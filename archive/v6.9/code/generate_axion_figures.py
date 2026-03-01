"""
KSAU v6.9: Experimental Signature Figures (Definitive Sync)
===========================================================
Generates the predicted Gamma spectrum and schematic
for the 0.392 MeV Geometric Axion.
"""
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

# Add v6.0 code path for config
sys.path.append(os.path.abspath('v6.0/code'))
import ksau_config

def generate_axion_figures_definitive():
    print("="*60)
    print("KSAU v6.9: Signature Figure Synchronization")
    print("="*60)

    # 1. Calculate Target Mass from SSoT
    phys = ksau_config.load_physical_constants()
    topo = ksau_config.load_topology_assignments()
    kappa = ksau_config.KAPPA
    
    m_top = phys['quarks']['Top']['observed_mass']
    v_top = topo['Top']['volume']
    bq_top = np.log(m_top) - (10 * kappa * v_top)
    
    v_axion = 5.6930 # 6_3 knot
    m_axion = np.exp((10 * kappa) * v_axion + bq_top)
    print(f"Targeting Axion Mass: {m_axion:.4f} MeV")

    # 2. Plotting
    plt.style.use('seaborn-v0_8-paper')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # --- Plot A: Nuclear Gamma Spectrum ---
    # Centered around the new 0.392 MeV peak
    x = np.linspace(0.2, 0.6, 500)
    bg = 100 * np.exp(-2 * x)
    mu = m_axion
    sigma = 0.005 
    signal = 15 * np.exp(-(x - mu)**2 / (2 * sigma**2))

    ax1.plot(x, bg, color='gray', linestyle='--', label='Standard Background')
    ax1.plot(x, bg + signal, color='red', linewidth=2, label='KSAU Axion Signal')
    ax1.fill_between(x, bg, bg + signal, color='red', alpha=0.3)

    ax1.set_title('A: Predicted Nuclear Gamma Spectrum', fontsize=12)
    ax1.set_xlabel('Energy [MeV]', fontsize=10)
    ax1.set_ylabel('Events / bin', fontsize=10)
    ax1.axvline(mu, color='black', alpha=0.5, linestyle=':')
    ax1.text(mu + 0.01, 80, f'{mu:.3f} MeV Peak', color='red', fontweight='bold')
    ax1.legend()

    # --- Plot B: Beam Dump Schematic ---
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 5)
    ax2.axis('off')
    ax2.add_patch(plt.Rectangle((1, 2), 0.5, 1, color='gray'))
    ax2.text(1.25, 3.2, 'Target', ha='center')
    ax2.annotate('', xy=(1, 2.5), xytext=(0, 2.5), arrowprops=dict(arrowstyle='->', color='blue', lw=2))
    ax2.text(0.2, 2.7, 'e- Beam', color='blue')
    ax2.plot([1.5, 6], [2.5, 2.5], color='red', linestyle='--', alpha=0.5)
    ax2.text(3.5, 2.7, 'Geometric Axion (LLP)', color='red', fontsize=9)
    ax2.scatter([6], [2.5], color='red', s=100, marker='*')
    ax2.text(6, 2.8, 'Decay Vertex', ha='center', fontweight='bold')
    ax2.annotate('', xy=(8, 3.5), xytext=(6, 2.5), arrowprops=dict(arrowstyle='->', color='orange', lw=1.5))
    ax2.annotate('', xy=(8, 1.5), xytext=(6, 2.5), arrowprops=dict(arrowstyle='->', color='orange', lw=1.5))
    ax2.text(8.2, 3.6, r'$\gamma$')
    ax2.text(8.2, 1.4, r'$\gamma$')
    ax2.add_patch(plt.Rectangle((2, 0.5), 1, 4, color='black', alpha=0.2))
    ax2.text(2.5, 4.6, 'Shielding', ha='center')
    ax2.set_title('B: Beam Dump Signature (LLP)', fontsize=12, pad=20)

    plt.tight_layout()
    os.makedirs('v6.9/figures', exist_ok=True)
    plt.savefig('v6.9/figures/figure_2_signatures.png', dpi=300)
    print("Figure 2 saved to v6.9/figures/figure_2_signatures.png")

if __name__ == "__main__":
    generate_axion_figures_definitive()
