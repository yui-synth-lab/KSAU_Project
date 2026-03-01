import matplotlib.pyplot as plt
import numpy as np
import os
import ksau_config

def generate_cabibbo_plot():
    # 1. Load Data
    topo = ksau_config.load_topology_assignments()
    phys = ksau_config.load_physical_constants()
    ckm = np.array(phys['ckm']['matrix'])
    
    # Transitions of interest
    v_us_exp = ckm[0, 1]
    v_cb_exp = ckm[1, 2]
    V_exp = [v_us_exp, v_cb_exp]
    
    def get_v_metrics(q1, q2):
        v1 = topo[q1]['volume']
        v2 = topo[q2]['volume']
        return abs(v1 - v2), (v1 + v2) / 2.0

    dv_us, m_us = get_v_metrics('Up', 'Strange')
    dv_cb, m_cb = get_v_metrics('Charm', 'Bottom')
    
    Delta_V = [dv_us, dv_cb]
    Mean_V = [m_us, m_cb]

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 12))

    # ========== Panel 1: The Anomaly ==========
    ax1.scatter(Delta_V, V_exp, s=300, c=['#FF6B6B', '#4ECDC4'], 
                edgecolors='black', linewidths=2, zorder=3)
    ax1.plot([0.5, 3.5], [0.3, 0.05], 'k--', alpha=0.3, 
             label='Naive expectation\n(smaller delta V -> stronger mixing)')
    ax1.set_xlabel('delta V (Shape Dissimilarity)', fontsize=13, fontweight='bold')
    ax1.set_ylabel('|V_ij| (Mixing Strength)', fontsize=13, fontweight='bold')
    ax1.set_title('Panel A: The Cabibbo Anomaly', fontsize=15, fontweight='bold')
    ax1.annotate(f'Cabibbo: Strongest mixing\ndespite large delta V ({dv_us:.2f})', 
                 xy=(dv_us, v_us_exp), xytext=(dv_us - 1.2, v_us_exp + 0.02),
                 arrowprops=dict(arrowstyle='->', color='#FF6B6B', lw=3),
                 fontsize=11, color='#FF6B6B', fontweight='bold')
    ax1.legend(loc='upper right', fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0.5, 4.5)
    ax1.set_ylim(0, 0.3)

    # ========== Panel 2: The Resolution ==========
    ax2.scatter(Mean_V[0], V_exp[0], s=300, c='#FF6B6B', 
                edgecolors='black', linewidths=2, label='u->s (Quantum)', zorder=3)
    ax2.scatter(Mean_V[1], V_exp[1], s=300, c='#4ECDC4',
                edgecolors='black', linewidths=2, label='c->b (Classical)', zorder=3)

    V_range = np.linspace(7, 13, 100)
    tunneling = 0.3 * np.exp(-12.2 / V_range) # Based on final beta result
    ax2.plot(V_range, tunneling, 'r-', linewidth=3, alpha=0.7,
             label='Logit-Geometric Projection')

    ax2.set_xlabel('Mean V_bar (Mass Scale)', fontsize=13, fontweight='bold')
    ax2.set_ylabel('|V_ij|', fontsize=13, fontweight='bold')
    ax2.set_title('Panel B: Mass-Dependent Tunneling', 
                  fontsize=15, fontweight='bold')
    ax2.legend(loc='upper right', fontsize=10)
    ax2.grid(True, alpha=0.3)

    # ========== Panel 3: Holographic Duality & Performance ==========
    ax3.text(0.5, 0.85, 'HOLOGRAPHIC DUALITY (v6.0)', 
             ha='center', fontsize=16, fontweight='bold',
             transform=ax3.transAxes)

    # Performance Stats
    ax3.text(0.1, 0.65, 'QUARK SECTOR (Bulk)', fontsize=12, fontweight='bold', color='#FF6B6B', transform=ax3.transAxes)
    ax3.text(0.1, 0.58, 'R² = 0.999952 (Volume Law)', fontsize=11, transform=ax3.transAxes)
    ax3.text(0.1, 0.52, 'MAE = 1.88%', fontsize=11, transform=ax3.transAxes)

    ax3.text(0.1, 0.35, 'LEPTON SECTOR (Boundary)', fontsize=12, fontweight='bold', color='#4ECDC4', transform=ax3.transAxes)
    ax3.text(0.1, 0.28, 'R² = 0.999327 (Complexity Law)', fontsize=11, transform=ax3.transAxes)
    ax3.text(0.1, 0.22, 'Muon Error = -0.01%', fontsize=11, fontweight='bold', transform=ax3.transAxes)

    ax3.text(0.5, 0.05, f'kappa = pi/24', ha='center', fontsize=18,
             fontweight='bold', transform=ax3.transAxes,
             bbox=dict(boxstyle='round', facecolor='gold', alpha=0.5))

    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)
    ax3.axis('off')
    ax3.set_title('Panel C: Global Model Statistics', 
                  fontsize=15, fontweight='bold')

    # ========== Panel 4: Model Comparison ==========
    # Updated R2 values from logit audit
    models = ['Baseline\n(Volume Only)', 'Logit-Geometric\n(Full v6.0)']
    r2_values = [0.44, 0.67] 
    colors_bar = ['#CCCCCC', '#4ECDC4']

    bars = ax4.bar(models, r2_values, color=colors_bar, 
                   edgecolor='black', linewidth=2, width=0.6)

    for i, (bar, r2) in enumerate(zip(bars, r2_values)):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                 f'R² = {r2:.2f}',
                 ha='center', va='bottom', fontsize=14, fontweight='bold')

    ax4.set_ylabel('Global CKM Fit Quality (R²)', fontsize=13, fontweight='bold')
    ax4.set_title('Panel D: CKM Prediction Improvement', 
                  fontsize=15, fontweight='bold')
    ax4.set_ylim(0, 1.0)
    ax4.grid(True, axis='y', alpha=0.3)

    plt.tight_layout()
    output_dir = os.path.join('v6.0', 'figures')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'ksau_cabibbo_holographic.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Figure saved to {output_path}")

if __name__ == "__main__":
    generate_cabibbo_plot()
