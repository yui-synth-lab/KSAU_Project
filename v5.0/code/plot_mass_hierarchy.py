"""
KSAU v5.0: Mass Hierarchy Visualization
Generates publication-quality figures for the paper.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Set publication quality defaults
rcParams['font.family'] = 'serif'
rcParams['font.size'] = 10
rcParams['axes.labelsize'] = 11
rcParams['axes.titlesize'] = 12
rcParams['xtick.labelsize'] = 9
rcParams['ytick.labelsize'] = 9
rcParams['legend.fontsize'] = 9
rcParams['figure.dpi'] = 300

# Constants
KAPPA = np.pi / 24

# Data from v5.0 (with Twist correction)
PARTICLES = [
    'Up', 'Down', 'Strange', 'Charm', 'Bottom', 'Top',
    'Electron', 'Muon', 'Tau'
]

MASSES_OBS = np.array([
    2.16, 4.67, 93.4, 1270.0, 4180.0, 172760.0,
    0.510998, 105.658, 1776.86
])

MASSES_PRED = np.array([
    2.35, 4.69, 95.68, 1286.16, 3959.40, 153659.55,
    0.510998, 105.608, 1760.72
])

ERRORS = (MASSES_PRED - MASSES_OBS) / MASSES_OBS * 100

COLORS = {
    'quark': '#2E86AB',
    'lepton': '#A23B72',
    'up-type': '#06A77D',
    'down-type': '#D84A05'
}


def plot_mass_spectrum():
    """Figure 1: Mass spectrum with predictions."""
    fig, ax = plt.subplots(figsize=(8, 5))

    x = np.arange(len(PARTICLES))
    width = 0.35

    # Separate quarks and leptons
    quark_mask = np.array([True]*6 + [False]*3)
    lepton_mask = ~quark_mask

    # Plot quarks
    ax.bar(x[quark_mask] - width/2, MASSES_OBS[quark_mask], width,
           label='Observed (Quarks)', color=COLORS['quark'], alpha=0.7)
    ax.bar(x[quark_mask] + width/2, MASSES_PRED[quark_mask], width,
           label='Predicted (Quarks)', color=COLORS['quark'],
           alpha=0.4, edgecolor=COLORS['quark'], linewidth=1.5)

    # Plot leptons
    ax.bar(x[lepton_mask] - width/2, MASSES_OBS[lepton_mask], width,
           label='Observed (Leptons)', color=COLORS['lepton'], alpha=0.7)
    ax.bar(x[lepton_mask] + width/2, MASSES_PRED[lepton_mask], width,
           label='Predicted (Leptons)', color=COLORS['lepton'],
           alpha=0.4, edgecolor=COLORS['lepton'], linewidth=1.5)

    ax.set_ylabel('Mass (MeV)', fontweight='bold')
    ax.set_xlabel('Particle', fontweight='bold')
    ax.set_title('KSAU v5.0: Fermion Mass Predictions', fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(PARTICLES, rotation=45, ha='right')
    ax.set_yscale('log')
    ax.legend(loc='upper left', framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')

    plt.tight_layout()
    plt.savefig('../figures/figure1_mass_spectrum.png', dpi=300, bbox_inches='tight')
    print("Saved: ../figures/figure1_mass_spectrum.png")
    plt.close()


def plot_error_comparison():
    """Figure 2: Error comparison across versions."""
    # Data for different versions
    versions = ['v4.1\n(G only)', 'v5.0\n(no Twist)', 'v5.0\n(with Twist)']

    # MAE values
    quark_mae = [6.65, 6.86, 4.84]
    lepton_mae = [0.48, 0.32, 0.32]
    global_mae = [4.59, 4.68, 3.33]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    # Left panel: MAE by category
    x = np.arange(len(versions))
    width = 0.25

    ax1.bar(x - width, quark_mae, width, label='Quark MAE',
            color=COLORS['quark'], alpha=0.7)
    ax1.bar(x, lepton_mae, width, label='Lepton MAE',
            color=COLORS['lepton'], alpha=0.7)
    ax1.bar(x + width, global_mae, width, label='Global MAE',
            color='gray', alpha=0.7)

    ax1.set_ylabel('Mean Absolute Error (%)', fontweight='bold')
    ax1.set_xlabel('Version', fontweight='bold')
    ax1.set_title('Performance Evolution', fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(versions)
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.set_ylim(0, 8)

    # Add target line at 5%
    ax1.axhline(y=5, color='red', linestyle='--', linewidth=1,
                label='Target (5%)', alpha=0.5)

    # Right panel: Individual particle errors (v5.0 with Twist)
    colors = [COLORS['quark']]*6 + [COLORS['lepton']]*3
    bars = ax2.barh(PARTICLES, ERRORS, color=colors, alpha=0.7)

    ax2.set_xlabel('Prediction Error (%)', fontweight='bold')
    ax2.set_title('v5.0 Individual Errors (with Twist)', fontweight='bold')
    ax2.axvline(x=0, color='black', linewidth=0.8)
    ax2.grid(True, alpha=0.3, axis='x')

    # Color bars by sign
    for i, (bar, err) in enumerate(zip(bars, ERRORS)):
        if err < 0:
            bar.set_edgecolor('blue')
            bar.set_linewidth(1.5)
        else:
            bar.set_edgecolor('red')
            bar.set_linewidth(1.5)

    plt.tight_layout()
    plt.savefig('../figures/figure2_error_comparison.png', dpi=300, bbox_inches='tight')
    print("Saved: ../figures/figure2_error_comparison.png")
    plt.close()


def plot_twist_effect():
    """Figure 3: Impact of Twist correction on quarks."""
    # Errors without Twist (from the comparison)
    errors_no_twist = {
        'Down': 14.44,
        'Bottom': -16.90,
        'Up': -4.72,
        'Top': 1.38,
        'Strange': 2.45,  # unchanged
        'Charm': 1.27     # unchanged
    }

    # Errors with Twist
    errors_with_twist = {
        'Down': 0.40,
        'Bottom': -5.28,
        'Up': 8.61,
        'Top': -11.06,
        'Strange': 2.45,
        'Charm': 1.27
    }

    quarks = ['Up', 'Down', 'Strange', 'Charm', 'Bottom', 'Top']

    fig, ax = plt.subplots(figsize=(8, 5))

    x = np.arange(len(quarks))
    width = 0.35

    no_twist = [errors_no_twist[q] for q in quarks]
    with_twist = [errors_with_twist[q] for q in quarks]

    ax.bar(x - width/2, no_twist, width, label='Without Twist',
           color='gray', alpha=0.6)
    ax.bar(x + width/2, with_twist, width, label='With Twist',
           color=COLORS['quark'], alpha=0.8)

    ax.set_ylabel('Prediction Error (%)', fontweight='bold')
    ax.set_xlabel('Quark', fontweight='bold')
    ax.set_title('Effect of Twist Correction', fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(quarks)
    ax.axhline(y=0, color='black', linewidth=0.8)
    ax.axhline(y=5, color='green', linestyle='--', linewidth=1, alpha=0.5)
    ax.axhline(y=-5, color='green', linestyle='--', linewidth=1, alpha=0.5)
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3, axis='y')

    # Annotate improvements
    for i, q in enumerate(quarks):
        if abs(no_twist[i]) > abs(with_twist[i]) + 2:  # significant improvement
            improvement = abs(no_twist[i]) - abs(with_twist[i])
            ax.annotate(f'-{improvement:.1f}%',
                       xy=(i, max(no_twist[i], with_twist[i])),
                       xytext=(0, 5), textcoords='offset points',
                       ha='center', fontsize=8, color='green',
                       weight='bold')

    plt.tight_layout()
    plt.savefig('../figures/figure3_twist_effect.png', dpi=300, bbox_inches='tight')
    print("Saved: ../figures/figure3_twist_effect.png")
    plt.close()


def plot_volume_mass_correlation():
    """Figure 4: Hyperbolic volume vs log(mass)."""
    # Quark data
    quark_volumes = np.array([6.599, 7.328, 9.532, 11.517, 12.276, 15.271])
    quark_masses = MASSES_OBS[:6]
    quark_names = PARTICLES[:6]

    # Lepton data (N^2 as proxy)
    lepton_n2 = np.array([9, 36, 49])
    lepton_masses = MASSES_OBS[6:]
    lepton_names = PARTICLES[6:]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    # Quarks: Volume vs log(mass)
    ax1.scatter(quark_volumes, np.log(quark_masses),
               s=100, color=COLORS['quark'], alpha=0.7, edgecolors='black')

    # Fit line
    V_fit = np.linspace(6, 16, 100)
    log_m_fit = 10 * KAPPA * V_fit - (7 + 7*KAPPA)
    ax1.plot(V_fit, log_m_fit, 'r--', linewidth=2, alpha=0.7,
            label=r'$\ln(m) = 10\kappa \cdot V + \kappa \cdot \mathcal{T} - (7+7\kappa)$')

    # Annotate points
    for i, name in enumerate(quark_names):
        ax1.annotate(name, (quark_volumes[i], np.log(quark_masses[i])),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=9, weight='bold')

    ax1.set_xlabel('Hyperbolic Volume $V$', fontweight='bold')
    ax1.set_ylabel(r'$\ln(m / \mathrm{MeV})$', fontweight='bold')
    ax1.set_title('Quarks: Volume-Mass Correlation', fontweight='bold')
    ax1.legend(loc='upper left', fontsize=8)
    ax1.grid(True, alpha=0.3)

    # Leptons: N^2 vs log(mass)
    ax2.scatter(lepton_n2, np.log(lepton_masses),
               s=100, color=COLORS['lepton'], alpha=0.7, edgecolors='black')

    # Fit line
    N2_fit = np.linspace(0, 60, 100)
    gamma_l = (14/9) * KAPPA
    C_l = np.log(MASSES_OBS[6]) - gamma_l * 9  # calibrated to electron
    log_m_fit_l = gamma_l * N2_fit + C_l
    ax2.plot(N2_fit, log_m_fit_l, 'r--', linewidth=2, alpha=0.7,
            label=r'$\ln(m) = \frac{14}{9}\kappa \cdot N^2 + C_l$')

    # Annotate points
    for i, name in enumerate(lepton_names):
        ax2.annotate(name, (lepton_n2[i], np.log(lepton_masses[i])),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=9, weight='bold')

    ax2.set_xlabel('Crossing Number Squared $N^2$', fontweight='bold')
    ax2.set_ylabel(r'$\ln(m / \mathrm{MeV})$', fontweight='bold')
    ax2.set_title('Leptons: $N^2$-Mass Correlation', fontweight='bold')
    ax2.legend(loc='upper left', fontsize=8)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('../figures/figure4_correlation.png', dpi=300, bbox_inches='tight')
    print("Saved: ../figures/figure4_correlation.png")
    plt.close()


def plot_catalan_identity():
    """Figure 5: Visualization of G ~ 7π/24 identity."""
    from matplotlib.patches import Rectangle

    fig, ax = plt.subplots(figsize=(10, 6))

    # Values
    G = 0.915965594177219
    approx = 7 * np.pi / 24

    # Create bars
    bars = ax.barh(['Catalan\nConstant G', '7π/24\nApproximation'],
                   [G, approx],
                   color=['#E63946', '#457B9D'],
                   alpha=0.8,
                   edgecolor='black',
                   linewidth=1.5)

    # Add values as text
    ax.text(G/2, 0, f'{G:.10f}',
           ha='center', va='center', fontsize=11, weight='bold', color='white')
    ax.text(approx/2, 1, f'{approx:.10f}',
           ha='center', va='center', fontsize=11, weight='bold', color='white')

    # Add difference
    diff = abs(G - approx)
    rel_err = diff / G * 100

    ax.text(0.92, 0.5, f'Δ = {diff:.6f}\n({rel_err:.3f}%)',
           ha='left', va='center', fontsize=10,
           bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))

    ax.set_xlabel('Value', fontweight='bold', fontsize=12)
    ax.set_title('Catalan Constant Identity: $G \\approx 7\\pi/24$',
                fontweight='bold', fontsize=14, pad=15)
    ax.set_xlim(0, 1.0)
    ax.grid(True, alpha=0.3, axis='x')

    plt.tight_layout()
    plt.savefig('../figures/figure5_catalan_identity.png', dpi=300, bbox_inches='tight')
    print("Saved: ../figures/figure5_catalan_identity.png")
    plt.close()


def plot_determinant_rules():
    """Figure 6: Binary determinant pattern for down-type quarks."""
    import matplotlib.patches as mpatches

    fig, ax = plt.subplots(figsize=(8, 5))

    # Particle data
    particles = {
        'Up': {'Det': 18, 'Type': 'up', 'Gen': 1, 'y': 3},
        'Charm': {'Det': 12, 'Type': 'up', 'Gen': 2, 'y': 2},
        'Top': {'Det': 114, 'Type': 'up', 'Gen': 3, 'y': 1},
        'Down': {'Det': 16, 'Type': 'down', 'Gen': 1, 'y': 3, 'k': 4},
        'Strange': {'Det': 32, 'Type': 'down', 'Gen': 2, 'y': 2, 'k': 5},
        'Bottom': {'Det': 64, 'Type': 'down', 'Gen': 3, 'y': 1, 'k': 6}
    }

    for name, data in particles.items():
        det = data['Det']
        y = data['y']
        color = COLORS['up-type'] if data['Type'] == 'up' else COLORS['down-type']

        # Plot point
        ax.scatter(det, y, s=200, color=color, alpha=0.8,
                  edgecolors='black', linewidth=2, zorder=3)

        # Label
        if data['Type'] == 'down':
            label = f"{name}\nDet={det}\n$2^{data['k']}$"
        else:
            label = f"{name}\nDet={det}\n(even)"

        ax.text(det, y, label, ha='center', va='center',
               fontsize=8, weight='bold', color='white')

    ax.set_xlabel('Determinant', fontweight='bold', fontsize=12)
    ax.set_ylabel('Generation', fontweight='bold', fontsize=12)
    ax.set_title('Binary Determinant Rule: Down-type Quarks',
                fontweight='bold', fontsize=13, pad=15)
    ax.set_yticks([1, 2, 3])
    ax.set_yticklabels(['Gen 3', 'Gen 2', 'Gen 1'])
    ax.set_xlim(0, 120)
    ax.set_ylim(0.5, 3.5)
    ax.grid(True, alpha=0.3)

    # Legend
    up_patch = mpatches.Patch(color=COLORS['up-type'], label='Up-type (even Det)')
    down_patch = mpatches.Patch(color=COLORS['down-type'], label='Down-type ($2^k$)')
    ax.legend(handles=[up_patch, down_patch], loc='upper left', fontsize=10)

    # Annotate binary sequence
    ax.text(48, 0.8, 'Binary Sequence: $2^4, 2^5, 2^6 = 16, 32, 64$',
           ha='center', fontsize=10, style='italic',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    plt.savefig('../figures/figure6_determinant_rules.png', dpi=300, bbox_inches='tight')
    print("Saved: ../figures/figure6_determinant_rules.png")
    plt.close()


if __name__ == "__main__":
    print("="*60)
    print("KSAU v5.0: Generating Publication Figures")
    print("="*60)
    print()

    plot_mass_spectrum()
    plot_error_comparison()
    plot_twist_effect()
    plot_volume_mass_correlation()
    plot_catalan_identity()
    plot_determinant_rules()

    print()
    print("="*60)
    print("All figures generated successfully!")
    print("="*60)
