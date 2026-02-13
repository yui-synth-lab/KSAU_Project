"""
KSAU v6.9: Mass Spectrum & Axion Prediction (Definitive Sync)
===========================================================
Dynamically loads all Standard Model data from v6.0 SSoT
and projects the 6_3 Geometric Axion.
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys
import os

# Add v6.0 code path for config
sys.path.append(os.path.abspath('v6.0/code'))
import ksau_config

def generate_spectrum_definitive():
    print("="*60)
    print("KSAU v6.9: Final Spectrum Synchronization")
    print("="*60)

    # 1. Load Data
    phys = ksau_config.load_physical_constants()
    topo = ksau_config.load_topology_assignments()
    kappa = ksau_config.KAPPA
    bq = -(7 + 7 * kappa)

    # 2. Prepare Data Points from SSoT
    plot_data = []
    
    # Standard Model Particles
    for p_name, data in topo.items():
        # Get category
        if p_name in ['Electron', 'Muon', 'Tau']:
            group = 'Lepton'
            m_obs = phys['leptons'][p_name]['observed_mass']
        elif p_name in ['Up', 'Down', 'Strange', 'Charm', 'Bottom', 'Top']:
            group = 'Quark'
            m_obs = phys['quarks'][p_name]['observed_mass']
        else:
            group = 'Boson'
            m_obs = phys['bosons'][p_name]['observed_mass']
            
        plot_data.append({
            'name': p_name,
            'mass': m_obs,
            'vol': data['volume'],
            'type': group
        })

    # 3. PREDICTION: Geometric Axion (6_3 knot)
    v_axion = 5.6930 # 6_3 knot volume
    
    # BULK LAW SYNC (Top-referenced intercept Bq)
    # Using the current best fit from Phase 3 synchronization:
    m_top_obs = phys['quarks']['Top']['observed_mass']
    v_top = topo['Top']['volume']
    bq_top = np.log(m_top_obs) - (10 * kappa * v_top)
    
    # m_axion = exp(10*kappa * V_axion + Bq)
    ln_ma = (10 * kappa) * v_axion + bq_top
    m_axion = np.exp(ln_ma)
    
    plot_data.append({
        'name': 'Axion (6_3)',
        'mass': m_axion,
        'vol': v_axion,
        'type': 'Prediction'
    })

    df = pd.DataFrame(plot_data)
    print(f"Top-referenced Bq: {bq_top:.4f}")
    print(f"Calculated Axion Mass: {m_axion:.4f} MeV")

    # 4. PLOTTING
    plt.style.use('seaborn-v0_8-paper')
    fig, ax = plt.subplots(figsize=(10, 7))

    # Groups
    leptons = df[df['type'] == 'Lepton']
    quarks = df[df['type'] == 'Quark']
    bosons = df[df['type'] == 'Boson']
    pred = df[df['type'] == 'Prediction']

    # Scatter Points
    ax.scatter(leptons['vol'], leptons['mass'], color='blue', marker='o', s=100, label='Leptons', zorder=3)
    ax.scatter(quarks['vol'], quarks['mass'], color='green', marker='s', s=100, label='Quarks', zorder=3)
    ax.scatter(bosons['vol'], bosons['mass'], color='purple', marker='^', s=100, label='Bosons', zorder=3)
    ax.scatter(pred['vol'], pred['mass'], color='red', marker='*', s=400, label='Axion Prediction', zorder=10, edgecolor='black')

    # Annotations
    for _, row in df.iterrows():
        if row['type'] == 'Prediction':
            label = f"{row['name']}\n{row['mass']:.3f} MeV"
            ax.annotate(label, (row['vol'], row['mass']), xytext=(row['vol']+1, row['mass']*0.5),
                        arrowprops=dict(arrowstyle='->', color='red'), fontsize=12, color='red', fontweight='bold')
        else:
            ax.text(row['vol']+0.2, row['mass']*0.8, row['name'], fontsize=9)

    # Scaling Lines (Bulk)
    v_range = np.linspace(0, 20, 100)
    ax.plot(v_range, np.exp((10*kappa)*v_range + bq), '--', color='black', alpha=0.2, label='Bulk Scaling Law')

    ax.set_yscale('log')
    ax.set_xlabel('Hyperbolic Volume (V)', fontsize=12)
    ax.set_ylabel('Mass [MeV]', fontsize=12)
    ax.set_title('Figure 1: KSAU Mass Spectrum & Definitive Axion Prediction', fontsize=14, fontweight='bold')
    ax.grid(True, which="both", ls="-", alpha=0.2)
    ax.legend(loc='lower right')

    plt.tight_layout()
    os.makedirs('v6.9/figures', exist_ok=True)
    plt.savefig('v6.9/figures/figure_1_spectrum.png', dpi=300)
    print("Figure 1 saved to v6.9/figures/figure_1_spectrum.png")

if __name__ == "__main__":
    generate_spectrum_definitive()
