import matplotlib.pyplot as plt
import numpy as np

# Set style
plt.style.use('seaborn-v0_8-paper')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# --- Plot A: Nuclear Gamma Spectrum ---
x = np.linspace(0.4, 0.8, 500)
# Background (exponential decay-like)
bg = 100 * np.exp(-2 * x)
# Signal peak at 0.627 MeV
mu = 0.627
sigma = 0.005 # Energy resolution approx 1%
signal = 15 * np.exp(-(x - mu)**2 / (2 * sigma**2))

ax1.plot(x, bg, color='gray', linestyle='--', label='Standard Background')
ax1.plot(x, bg + signal, color='red', linewidth=2, label='KSAU Axion Signal')
ax1.fill_between(x, bg, bg + signal, color='red', alpha=0.3)

ax1.set_title('A: Predicted Nuclear Gamma Spectrum', fontsize=12)
ax1.set_xlabel('Energy [MeV]', fontsize=10)
ax1.set_ylabel('Events / bin', fontsize=10)
ax1.axvline(0.627, color='black', alpha=0.5, linestyle=':')
ax1.text(0.635, 80, '0.627 MeV Peak', color='red', fontweight='bold')
ax1.legend()

# --- Plot B: Beam Dump Schematic ---
# We'll draw a simple schematic using shapes
ax2.set_xlim(0, 10)
ax2.set_ylim(0, 5)
ax2.axis('off')

# Target
ax2.add_patch(plt.Rectangle((1, 2), 0.5, 1, color='gray'))
ax2.text(1.25, 3.2, 'Target', ha='center')

# Beam
ax2.annotate('', xy=(1, 2.5), xytext=(0, 2.5),
             arrowprops=dict(arrowstyle='->', color='blue', lw=2))
ax2.text(0.2, 2.7, 'e- Beam', color='blue')

# Axion path (invisible/dashed)
ax2.plot([1.5, 6], [2.5, 2.5], color='red', linestyle='--', alpha=0.5)
ax2.text(3.5, 2.7, 'Geometric Axion (LLP)', color='red', fontsize=9)

# Decay vertex
ax2.scatter([6], [2.5], color='red', s=100, marker='*')
ax2.text(6, 2.8, 'Decay Vertex', ha='center', fontweight='bold')

# Photons
ax2.annotate('', xy=(8, 3.5), xytext=(6, 2.5),
             arrowprops=dict(arrowstyle='->', color='orange', lw=1.5))
ax2.annotate('', xy=(8, 1.5), xytext=(6, 2.5),
             arrowprops=dict(arrowstyle='->', color='orange', lw=1.5))
ax2.text(8.2, 3.6, r'$\gamma$')
ax2.text(8.2, 1.4, r'$\gamma$')

# Shielding
ax2.add_patch(plt.Rectangle((2, 0.5), 1, 4, color='black', alpha=0.2))
ax2.text(2.5, 4.6, 'Shielding', ha='center')

ax2.set_title('B: Beam Dump Signature (LLP)', fontsize=12, pad=20)

plt.tight_layout()
plt.savefig('v6.9/figures/figure_2_signatures.png', dpi=300)
print("Figure 2 saved to v6.9/figures/figure_2_signatures.png")
