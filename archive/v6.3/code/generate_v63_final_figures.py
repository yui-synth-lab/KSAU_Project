import matplotlib.pyplot as plt
import numpy as np
import os
import sys

# Add v6.1 code to path for utils_v61
sys.path.append(os.path.join(os.path.dirname(__file__), '../../v6.1/code'))
import utils_v61

def generate_v63_plot():
    # Ensure directory exists
    os.makedirs('v6.3/figures', exist_ok=True)
    
    # Constants from config
    consts = utils_v61.load_constants()
    G = consts['G_catalan']
    kappa = consts['kappa']
    
    # Fermion Scaling (v6.0 Unified Law)
    A_f = 10 * kappa
    C_f = -(7 + 7 * kappa)
    
    # Boson Scaling (v6.3 Discovery)
    A_b = (3/7) * G
    # Derived from W-boson baseline from config
    m_w_obs = consts['bosons']['W']['observed_mass']
    # W volume from assignments
    topo = utils_v61.load_assignments()
    v_w = topo['W']['volume']
    C_b = np.log(m_w_obs) - A_b * v_w
    
    # Volume range
    v = np.linspace(2, 20, 400)
    ln_m_f = A_f * v + C_f
    ln_m_b = A_b * v + C_b
    
    plt.figure(figsize=(10, 7))
    
    # Plot Lines
    plt.plot(v, ln_m_f, 'b-', label='Fermions (Slope = 10/7 G)', linewidth=2)
    plt.plot(v, ln_m_b, 'r--', label='Bosons (Slope = 3/7 G)', linewidth=2)
    
    # Data Points: Fermions
    # Top Quark (V ~ 15.4)
    vt = 15.41
    plt.scatter([vt], [A_f * vt + C_f], color='blue', s=100, zorder=5)
    plt.annotate('Top Quark', (vt, A_f * vt + C_f), xytext=(10, -10), textcoords='offset points', fontsize=12, color='blue')
    
    # Data Points: Bosons
    bosons = [
        ('W', 14.655, 'red'),
        ('Z', 15.028, 'red'),
        ('Higgs', 15.821, 'darkred')
    ]
    for name, vb, color in bosons:
        plt.scatter([vb], [A_b * vb + C_b], color=color, s=100, zorder=5)
        plt.annotate(name, (vb, A_b * vb + C_b), xytext=(-20, 15), textcoords='offset points', fontsize=12, color=color)

    # Highlight Intersection Zone
    intersection_v = (C_b - C_f) / (A_f - A_b)
    plt.axvspan(intersection_v - 1, intersection_v + 1, color='gray', alpha=0.1, label='Interaction Zone')
    plt.scatter([intersection_v], [A_f * intersection_v + C_f], color='black', s=150, marker='X', zorder=6)
    
    plt.title('Figure 1: The Holographic Intersection (KSAU v6.3)', fontsize=16)
    plt.xlabel('Hyperbolic Volume (V)', fontsize=14)
    plt.ylabel('ln(Mass [MeV])', fontsize=14)
    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    plt.legend(fontsize=12)
    
    # Caption simulation in plot
    caption_text = (
        "The 'Magic Region' (V ~ 15): Where Matter (Fermions) and Force (Bosons) intersect.\n"
        "This geometric crossing enables Higgs coupling and Top-W flavor transitions."
    )
    plt.figtext(0.15, 0.02, caption_text, ha="left", fontsize=10, bbox={"facecolor":"orange", "alpha":0.1, "pad":5})

    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    
    # Save figure
    save_path = 'v6.3/figures/Fig1_Holographic_Intersection.png'
    plt.savefig(save_path, dpi=300)
    print(f"Graph generated and saved to: {save_path}")
    print(f"Calculated Intersection Volume: {intersection_v:.4f}")

if __name__ == "__main__":
    generate_v63_plot()