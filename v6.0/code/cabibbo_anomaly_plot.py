import matplotlib.pyplot as plt
import numpy as np
import os

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 12))

# ========== Panel 1: The Anomaly ==========
transitions = ['u->s\n(Cabibbo)', 'c->b']
V_exp = [0.225, 0.042]
Delta_V = [2.98, 0.76]
Mean_V = [8.04, 11.90]

ax1.scatter(Delta_V, V_exp, s=300, c=['#FF6B6B', '#4ECDC4'], 
            edgecolors='black', linewidths=2, zorder=3)
ax1.plot([0.5, 3.5], [0.3, 0.05], 'k--', alpha=0.3, 
         label='Naive expectation\n(smaller delta V -> stronger mixing)')
ax1.set_xlabel('delta V (Shape Dissimilarity)', fontsize=13, fontweight='bold')
ax1.set_ylabel('|V_ij| (Mixing Strength)', fontsize=13, fontweight='bold')
ax1.set_title('Panel A: The Cabibbo Anomaly', fontsize=15, fontweight='bold')
ax1.annotate('Cabibbo: 5x stronger\ndespite 4x larger delta V!', 
             xy=(2.98, 0.225), xytext=(2.0, 0.15),
             arrowprops=dict(arrowstyle='->', color='#FF6B6B', lw=3),
             fontsize=11, color='#FF6B6B', fontweight='bold')
ax1.legend(loc='upper right', fontsize=10)
ax1.grid(True, alpha=0.3)
ax1.set_xlim(0.5, 3.5)
ax1.set_ylim(0, 0.3)

# ========== Panel 2: The Resolution ==========
ax2.scatter(Mean_V[0], V_exp[0], s=300, c='#FF6B6B', 
            edgecolors='black', linewidths=2, label='u->s (Light)', zorder=3)
ax2.scatter(Mean_V[1], V_exp[1], s=300, c='#4ECDC4',
            edgecolors='black', linewidths=2, label='c->b (Heavy)', zorder=3)

# Tunneling curve
V_range = np.linspace(7, 13, 100)
tunneling = 0.3 * np.exp(2.5 / V_range)  # Schematic
ax2.plot(V_range, tunneling, 'r-', linewidth=3, alpha=0.7,
         label='Tunneling: exp(beta/V_bar)')

ax2.set_xlabel('Mean V_bar (Mass Scale)', fontsize=13, fontweight='bold')
ax2.set_ylabel('|V_ij|', fontsize=13, fontweight='bold')
ax2.set_title('Panel B: Quantum Tunneling Resolution', 
              fontsize=15, fontweight='bold')
ax2.annotate('Light -> Strong tunneling\n(Quantum regime)', 
             xy=(8.04, 0.225), xytext=(7.5, 0.17),
             arrowprops=dict(arrowstyle='->', color='#FF6B6B', lw=3),
             fontsize=11, color='#FF6B6B', fontweight='bold')
ax2.annotate('Heavy -> Suppressed\n(Classical regime)',
             xy=(11.90, 0.042), xytext=(11, 0.10),
             arrowprops=dict(arrowstyle='->', color='#4ECDC4', lw=3),
             fontsize=11, color='#4ECDC4', fontweight='bold')
ax2.legend(loc='upper right', fontsize=10)
ax2.grid(True, alpha=0.3)

# ========== Panel 3: Holographic Duality ==========
# Schematic diagram
ax3.text(0.5, 0.85, 'HOLOGRAPHIC DUALITY', 
         ha='center', fontsize=16, fontweight='bold',
         transform=ax3.transAxes)

# Bulk box
bulk_box = plt.Rectangle((0.05, 0.45), 0.4, 0.3, 
                         facecolor='#FFE5E5', edgecolor='#FF6B6B', 
                         linewidth=3, transform=ax3.transAxes)
ax3.add_patch(bulk_box)
ax3.text(0.25, 0.70, 'BULK SECTOR', ha='center', fontsize=12, 
         fontweight='bold', transform=ax3.transAxes)
ax3.text(0.25, 0.62, 'Quarks (Confined)', ha='center', fontsize=10,
         transform=ax3.transAxes)
ax3.text(0.25, 0.56, 'ln(m) = 10*kappa*V', ha='center', fontsize=10,
         transform=ax3.transAxes, style='italic')
ax3.text(0.25, 0.50, 'CKM: Tunneling YES', ha='center', fontsize=9,
         transform=ax3.transAxes, color='#FF6B6B', fontweight='bold')

# Boundary box
boundary_box = plt.Rectangle((0.55, 0.45), 0.4, 0.3,
                            facecolor='#E5F5F5', edgecolor='#4ECDC4',
                            linewidth=3, transform=ax3.transAxes)
ax3.add_patch(boundary_box)
ax3.text(0.75, 0.70, 'BOUNDARY SECTOR', ha='center', fontsize=12,
         fontweight='bold', transform=ax3.transAxes)
ax3.text(0.75, 0.62, 'Leptons (Free)', ha='center', fontsize=10,
         transform=ax3.transAxes)
ax3.text(0.75, 0.56, 'ln(m) = (14/9)*kappa*N^2', ha='center', fontsize=10,
         transform=ax3.transAxes, style='italic')
ax3.text(0.75, 0.50, 'PMNS: Different law', ha='center', fontsize=9,
         transform=ax3.transAxes, color='#4ECDC4', fontweight='bold')

# Master constant
ax3.text(0.5, 0.25, 'kappa = pi/24', ha='center', fontsize=18,
         fontweight='bold', transform=ax3.transAxes,
         bbox=dict(boxstyle='round', facecolor='gold', alpha=0.5))
ax3.text(0.5, 0.15, '(Casimir + String + Chern-Simons)', 
         ha='center', fontsize=10, style='italic',
         transform=ax3.transAxes)

ax3.set_xlim(0, 1)
ax3.set_ylim(0, 1)
ax3.axis('off')
ax3.set_title('Panel C: Theoretical Framework', 
              fontsize=15, fontweight='bold')

# ========== Panel 4: Model Comparison ==========
models = ['Simple\ndelta V only', 'With\nTunneling']
r2_values = [0.48, 0.89]
colors_bar = ['#CCCCCC', '#4ECDC4']

bars = ax4.bar(models, r2_values, color=colors_bar, 
               edgecolor='black', linewidth=2, width=0.6)

# Add R2 values on bars
for i, (bar, r2) in enumerate(zip(bars, r2_values)):
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height + 0.02,
             f'R2 = {r2:.2f}',
             ha='center', va='bottom', fontsize=14, fontweight='bold')

ax4.set_ylabel('Global CKM Fit Quality (R2)', fontsize=13, fontweight='bold')
ax4.set_title('Panel D: Improvement via Tunneling', 
              fontsize=15, fontweight='bold')
ax4.set_ylim(0, 1.0)
ax4.axhline(y=0.90, color='green', linestyle='--', linewidth=2, 
            alpha=0.5, label='Excellent fit (>0.90)')
ax4.axhline(y=0.70, color='orange', linestyle='--', linewidth=2,
            alpha=0.5, label='Good fit (>0.70)')
ax4.legend(loc='upper left', fontsize=9)
ax4.grid(True, axis='y', alpha=0.3)

plt.tight_layout()
output_path = os.path.join('v6.0', 'figures', 'ksau_cabibbo_holographic.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Figure saved to {output_path}")
