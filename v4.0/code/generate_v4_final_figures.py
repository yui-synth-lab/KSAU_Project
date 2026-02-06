
import numpy as np
import matplotlib.pyplot as plt
import os
from matplotlib import rcParams

# Set styles
rcParams['font.family'] = 'serif'
rcParams['figure.dpi'] = 300
rcParams['axes.grid'] = True
rcParams['grid.alpha'] = 0.3

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(BASE_DIR, "..", "figures")
if not os.path.exists(FIG_DIR):
    os.makedirs(FIG_DIR)

# Constants
G = 0.915965594
GAMMA_Q = (10/7) * G
B_PRIME = -(7 + G)
GAMMA_L = (2/9) * G
C_L = -2.50335 # Optimized across 3 leptons

# Data
QUARKS = {
    'd': {'m': 4.67, 'Q': -1/3, 'Det': 16, 'V': 7.327725}, # 8G
    's': {'m': 93.4, 'Q': -1/3, 'Det': 32, 'V': 9.5319},
    'b': {'m': 4180, 'Q': -1/3, 'Det': 64, 'V': 12.2762},
    'u': {'m': 2.16, 'Q': 2/3, 'Det': 18, 'V': 6.598952},
    'c': {'m': 1270, 'Q': 2/3, 'Det': 12, 'V': 11.517101},
    't': {'m': 172760, 'Q': 2/3, 'Det': 124, 'V': 15.359984}
}

LEPTONS = {
    'e': {'m': 0.511, 'Q': -1, 'Det': 3, 'N2': 9},
    'mu': {'m': 105.66, 'Q': -1, 'Det': 9, 'N2': 36},
    'tau': {'m': 1776.86, 'Q': -1, 'Det': 7, 'N2': 49}
}

def plot_charge_determinant_rule():
    plt.figure(figsize=(10, 6))
    
    # Quarks (Even Det)
    q_dets = [d['Det'] for d in QUARKS.values()]
    q_charges = [d['Q'] for d in QUARKS.values()]
    q_labels = list(QUARKS.keys())
    
    # Leptons (Odd Det)
    l_dets = [d['Det'] for d in LEPTONS.values()]
    l_charges = [d['Q'] for d in LEPTONS.values()]
    l_labels = list(LEPTONS.keys())

    # Plot
    plt.scatter(q_charges, q_dets, s=150, c='red', marker='s', label='Quarks (Links)')
    plt.scatter(l_charges, l_dets, s=150, c='blue', marker='o', label='Leptons (Knots)')
    
    # Annotate
    for i, txt in enumerate(q_labels):
        plt.annotate(txt.upper(), (q_charges[i], q_dets[i]), xytext=(0, 10), 
                     textcoords='offset points', ha='center', fontweight='bold')
        
    for i, txt in enumerate(l_labels):
        plt.annotate(txt.upper(), (l_charges[i], l_dets[i]), xytext=(0, 10), 
                     textcoords='offset points', ha='center', fontweight='bold')

    # Highlights
    plt.axhline(0, color='black', linewidth=0.5)
    plt.axvline(0, color='black', linewidth=0.5)
    
    # Zones
    plt.text(0.15, 100, "Fractional Charge\nEVEN Determinant", fontsize=12, color='red', ha='center', bbox=dict(facecolor='white', alpha=0.8))
    plt.text(-0.65, 20, "Integer Charge\nODD Determinant", fontsize=12, color='blue', ha='center', bbox=dict(facecolor='white', alpha=0.8))
    
    plt.xlabel('Electric Charge (Q)', fontsize=12)
    plt.ylabel('Determinant (Det)', fontsize=12)
    plt.title('KSAU v4.0: The Charge-Determinant Parity Rule', fontsize=14, fontweight='bold')
    plt.yscale('log')
    plt.grid(True, which="both", ls="--")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, 'Fig1_Charge_Determinant_Rule.png'))
    plt.close()

def plot_down_quark_binary_rule():
    plt.figure(figsize=(8, 6))
    
    downs = ['d', 's', 'b']
    dets = [QUARKS[q]['Det'] for q in downs]
    gens = [1, 2, 3] # Generations
    
    plt.plot(gens, dets, 'ro-', linewidth=2, markersize=10, label='Down-type Determinants')
    
    # Theoretical 2^(3+g) or 2^(g+3)?
    # d(g=1)->16=2^4. s(g=2)->32=2^5. b(g=3)->64=2^6.
    # Formula: Det = 2^(Generation + 3)
    
    x_range = np.linspace(0.8, 3.2, 100)
    plt.plot(x_range, 2**(x_range+3), 'k--', alpha=0.5, label='Theory: $2^{Gen+3}$')
    
    for i, txt in enumerate(downs):
        plt.annotate(f"{txt.upper()} ({dets[i]})", (gens[i], dets[i]), xytext=(-10, 10), 
                     textcoords='offset points', fontweight='bold', fontsize=12)

    plt.yscale('log', base=2)
    plt.yticks([16, 32, 64, 128], ['16 ($2^4$)', '32 ($2^5$)', '64 ($2^6$)', '128 ($2^7$)'])
    plt.xlabel('Generation', fontsize=12)
    plt.ylabel('Determinant (Log Scale)', fontsize=12)
    plt.title('KSAU v4.0: The Binary Determinant Rule (Down-type)', fontsize=14, fontweight='bold')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, 'Fig2_Down_Binary_Rule.png'))
    plt.close()

def plot_unified_scaling():
    plt.figure(figsize=(10, 6))
    
    # Quarks
    q_vols = [d['V'] for d in QUARKS.values()]
    q_lnm = [np.log(d['m']) for d in QUARKS.values()]
    
    # Leptons (Map N^2 to Volume-equivalent for visualization?)
    # Or just plot predicted vs observed for both
    
    # Let's plot Predicted vs Observed Mass (Unified)
    
    # Quark Preds
    q_pred = [np.exp(GAMMA_Q * d['V'] + B_PRIME) for d in QUARKS.values()]
    q_obs = [d['m'] for d in QUARKS.values()]
    
    # Lepton Preds
    l_pred = [np.exp(GAMMA_L * d['N2'] + C_L) for d in LEPTONS.values()]
    l_obs = [d['m'] for d in LEPTONS.values()]
    
    all_obs = sorted(l_obs + q_obs)
    plt.loglog([all_obs[0]*0.5, all_obs[-1]*2], [all_obs[0]*0.5, all_obs[-1]*2], 'k-', alpha=0.2, label='Identity')

    plt.scatter(q_obs, q_pred, c='red', marker='s', s=100, zorder=5, label='Quarks (7D Channel)')
    plt.scatter(l_obs, l_pred, c='blue', marker='o', s=100, zorder=5, label='Leptons (9D Channel)')

    # Annotate with offsets to avoid overlap
    q_offsets = {'d': (8, 5), 's': (8, -2), 'b': (8, 5), 'u': (8, -8), 'c': (8, 5), 't': (8, 5)}
    for i, q in enumerate(QUARKS.keys()):
        ox, oy = q_offsets.get(q, (5, -5))
        plt.annotate(q.upper(), (q_obs[i], q_pred[i]), xytext=(ox, oy), textcoords='offset points', fontweight='bold')

    l_offsets = {'e': (8, -2), 'mu': (-35, 8), 'tau': (8, -8)}
    for i, l in enumerate(LEPTONS.keys()):
        ox, oy = l_offsets.get(l, (5, -5))
        plt.annotate(l.upper(), (l_obs[i], l_pred[i]), xytext=(ox, oy), textcoords='offset points', fontweight='bold')
        
    plt.xlabel('Observed Mass (MeV)', fontsize=12)
    plt.ylabel('Predicted Mass (MeV)', fontsize=12)
    plt.title('KSAU v4.0: Unified Geometric Mass Generation', fontsize=14, fontweight='bold')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, 'Fig3_Unified_Scaling.png'))
    plt.close()

if __name__ == "__main__":
    print("Generating v4.0 Final Figures...")
    plot_charge_determinant_rule()
    plot_down_quark_binary_rule()
    plot_unified_scaling()
    print("Done: Figures Generated in v4.0/figures/")
