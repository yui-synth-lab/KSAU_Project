
import numpy as np
import json
from pathlib import Path
import matplotlib.pyplot as plt

def generate_landscape_plot():
    # Load v5.0 data
    json_path = Path('v5.0/data/topology_assignments.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    kappa = np.pi / 24
    bq = -(7 + 7 * kappa)
    
    quarks = ['Up', 'Down', 'Strange', 'Charm', 'Bottom', 'Top']
    v_ideal_list = []
    v_actual_list = []
    names = []
    
    for name in quarks:
        info = data[name]
        m_obs = info['observed_mass']
        v_actual = info['volume']
        gen = info['generation']
        comp = info['components']
        
        # Calculate Twist: (2 - Gen) * (-1)^Comp
        twist = (2 - gen) * ((-1)**comp)
        
        # Invert formula: ln(m) = 10*kappa*V + kappa*twist + Bq
        # V_ideal = (ln(m) - kappa*twist - Bq) / (10*kappa)
        v_ideal = (np.log(m_obs) - kappa*twist - bq) / (10 * kappa)
        
        v_ideal_list.append(v_ideal)
        v_actual_list.append(v_actual)
        names.append(name)

    # Plotting
    plt.figure(figsize=(10, 8))
    
    # y=x line (Ideal Continuum)
    max_v = max(v_ideal_list) * 1.1
    plt.plot([0, max_v], [0, max_v], 'k--', alpha=0.3, label='Ideal Continuum (No Noise)')
    
    # Scatter points
    colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#FFD700', '#FF6666']
    for i, name in enumerate(names):
        plt.scatter(v_ideal_list[i], v_actual_list[i], s=200, color=colors[i], 
                    edgecolors='black', zorder=5, label=name)
        
        # Draw the "Quantization Noise" line
        plt.plot([v_ideal_list[i], v_ideal_list[i]], [v_ideal_list[i], v_actual_list[i]], 
                 'r-', alpha=0.6, linewidth=2)
        
        # Annotate noise magnitude
        noise = v_actual_list[i] - v_ideal_list[i]
        plt.text(v_ideal_list[i] + 0.2, (v_ideal_list[i] + v_actual_list[i])/2, 
                 f'Noise: {noise:+.3f}', verticalalignment='center', fontsize=9)

    plt.xlabel('Required Ideal Volume (from Observed Mass)')
    plt.ylabel('Available Topological Volume (from Link Catalog)')
    plt.title('Topological Landscape: Quantization Noise Analysis')
    plt.legend()
    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    
    # Highlight Bottom Quark Gap
    plt.annotate('Quantization Gap\n(Missing Topology)', 
                 xy=(v_ideal_list[4], v_actual_list[4]), 
                 xytext=(v_ideal_list[4]-2, v_actual_list[4]+1.5),
                 arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=8),
                 fontsize=11, color='red', fontweight='bold')

    plt.savefig('v6.0/figures/topological_landscape.png', dpi=300)
    print("Topological Landscape plot saved to v6.0/figures/topological_landscape.png")

if __name__ == "__main__":
    generate_landscape_plot()
