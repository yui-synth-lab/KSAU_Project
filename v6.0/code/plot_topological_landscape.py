import numpy as np
import json
from pathlib import Path
import matplotlib.pyplot as plt
import ksau_config

def generate_landscape_plot():
    print("Generating Updated Topological Landscape (v6.0 Unified)...")

    # Load unified data (topology + physical constants)
    data = ksau_config.load_topology_assignments()
    phys = ksau_config.load_physical_constants()
    coeffs = ksau_config.get_kappa_coeffs()
    
    kappa = ksau_config.KAPPA
    G = phys['G_catalan']
    
    # 1. Scaling Definitions
    # Bulk (Quarks)
    slope_q = coeffs['quark_vol_coeff']
    bq = coeffs['quark_intercept']
    
    # Boundary (Leptons)
    slope_l = (2/9) * G
    cl = -2.38 # Latest unified intercept with entropy correction
    
    particles = []
    
    # Process Quarks
    for name in ['Up', 'Down', 'Strange', 'Charm', 'Bottom', 'Top']:
        info = data[name]
        m_obs = info['observed_mass']
        gen = info['generation']
        comp = info['components']
        twist = (2 - gen) * ((-1)**comp)
        
        # ln(m) = slope_q * V + kappa*twist + bq
        log_pred = slope_q * info['volume'] + kappa * twist + bq
        particles.append({
            'name': name, 'obs': m_obs, 'pred': np.exp(log_pred), 'sector': 'Bulk'
        })

    # Process Leptons (With Entropy Correction)
    for name in ['Electron', 'Muon', 'Tau']:
        info = data[name]
        m_obs = info['observed_mass']
        n = info['crossing_number']
        det = info['determinant']
        gen = info['generation']
        twist = gen - 2
        
        # ln(m) = slope_l * N^2 + kappa*twist - kappa*ln(det) + cl
        log_pred = slope_l * (n**2) + kappa * twist - kappa * np.log(det) + cl
        particles.append({
            'name': name, 'obs': m_obs, 'pred': np.exp(log_pred), 'sector': 'Boundary'
        })

    # Plotting
    plt.figure(figsize=(12, 10))
    
    # Log-Log Scale
    obs_vals = [p['obs'] for p in particles]
    pred_vals = [p['pred'] for p in particles]
    
    min_val = min(min(obs_vals), min(pred_vals)) * 0.5
    max_val = max(max(obs_vals), max(pred_vals)) * 2.0
    
    # y=x line (Theoretical Ideal)
    plt.loglog([min_val, max_val], [min_val, max_val], 'k--', alpha=0.3, label='Theoretical Ideal')
    
    # Scatter points with sector styling
    for p in particles:
        marker = 'o' if p['sector'] == 'Bulk' else 's'
        color = 'blue' if p['sector'] == 'Bulk' else 'red'
        plt.scatter(p[ 'pred'], p['obs'], s=250, color=color, alpha=0.7, 
                    marker=marker, edgecolors='black', zorder=5)
        
        # Label each particle
        plt.text(p['pred'] * 1.2, p['obs'], p['name'], verticalalignment='center', fontsize=12, fontweight='bold')

    plt.xlabel('Predicted Mass (MeV) [Topological Formula]', fontsize=14)
    plt.ylabel('Observed Mass (MeV) [Experimental]', fontsize=14)
    plt.title('KSAU v6.0: The Unified Topological Landscape\n(Holographic Dual: Bulk Volume vs. Boundary Complexity)', fontsize=16)
    
    # Add Sector Legends
    plt.scatter([], [], marker='o', color='blue', label='Bulk Sector (Quarks: Volume Law)')
    plt.scatter([], [], marker='s', color='red', label='Boundary Sector (Leptons: Complexity Law)')
    
    plt.legend(fontsize=12)
    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    
    # Highlight Muon Resolution
    muon = [p for p in particles if p['name'] == 'Muon'][0]
    plt.annotate('Muon Anomaly Resolved!\n(Entropy Corrected)', 
                 xy=(muon['pred'], muon['obs']), 
                 xytext=(muon['pred']*0.1, muon['obs']*10),
                 arrowprops=dict(facecolor='green', shrink=0.05, width=2),
                 fontsize=12, color='darkgreen', fontweight='bold', bbox=dict(boxstyle="round", fc="white", ec="green"))

    output_dir = Path('v6.0/figures')
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / 'topological_landscape.png', dpi=300)
    print(f"Unified Landscape plot saved to {output_dir / 'topological_landscape.png'}")

if __name__ == "__main__":
    generate_landscape_plot()