import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Set style
plt.style.use('seaborn-v0_8-paper')
fig, ax = plt.subplots(figsize=(10, 7))

# --- Data Preparation ---
data = [
    # Leptons (Boundary) - Effective scaling
    {'name': 'e',     'mass': 0.511,   'metric': 3.0, 'type': 'Lepton'},
    {'name': 'mu',    'mass': 105.66,  'metric': 9.0, 'type': 'Lepton'},
    {'name': 'tau',   'mass': 1776.86, 'metric': 11.0, 'type': 'Lepton'},
    
    # Quarks (Bulk) - Hyperbolic Volume
    {'name': 'd',     'mass': 4.7,     'metric': 2.0298, 'type': 'Quark'}, # 4_1
    {'name': 's',     'mass': 95.0,    'metric': 5.333, 'type': 'Quark'},  # 6^3_2 (approx)
    {'name': 'c',     'mass': 1275.0,  'metric': 11.0, 'type': 'Quark'},
    {'name': 'b',     'mass': 4180.0,  'metric': 13.5, 'type': 'Quark'},
    {'name': 't',     'mass': 173000.0,'metric': 18.5, 'type': 'Quark'},
    
    # Bosons
    {'name': 'W',     'mass': 80379.0, 'metric': 14.655, 'type': 'Boson'}, # L11n387
    {'name': 'Z',     'mass': 91187.6, 'metric': 15.027, 'type': 'Boson'}, # L11a431
    {'name': 'H',     'mass': 125100.0,'metric': 15.55, 'type': 'Boson'},
    
    # PREDICTION
    {'name': 'Axion (6_3)', 'mass': 0.627, 'metric': 5.693, 'type': 'Prediction'} # 6_3 Volume
]

df = pd.DataFrame(data)

# Separate groups for plotting
leptons = df[df['type'] == 'Lepton']
quarks = df[df['type'] == 'Quark']
bosons = df[df['type'] == 'Boson']
pred = df[df['type'] == 'Prediction']

# --- Plotting ---

# 1. Scaling Lines (Simplified visual fit)
x_lep = np.linspace(2, 12, 100)
p_lep = np.polyfit(leptons['metric'], np.log(leptons['mass']), 1)
y_lep = np.exp(p_lep[1]) * np.exp(p_lep[0] * x_lep)
ax.plot(x_lep, y_lep, '--', color='blue', alpha=0.3, label='Boundary Scaling (Leptons)')

bulk = pd.concat([quarks, bosons])
p_bulk = np.polyfit(bulk['metric'], np.log(bulk['mass']), 1)
x_bulk = np.linspace(0, 20, 100)
y_bulk = np.exp(p_bulk[1]) * np.exp(p_bulk[0] * x_bulk)
ax.plot(x_bulk, y_bulk, '-', color='black', alpha=0.3, label='Bulk Scaling (Quarks/Bosons)')

# 2. Scatter Points
ax.scatter(leptons['metric'], leptons['mass'], color='blue', marker='o', s=100, label='Leptons', zorder=3)
ax.scatter(quarks['metric'], quarks['mass'], color='green', marker='s', s=100, label='Quarks', zorder=3)
ax.scatter(bosons['metric'], bosons['mass'], color='purple', marker='^', s=100, label='Bosons', zorder=3)

# 3. The Prediction (Axion)
ax.scatter(pred['metric'], pred['mass'], color='red', marker='*', s=300, label='Axion Prediction', zorder=10, edgecolor='black')

# 4. Annotations
for i, row in df.iterrows():
    if row['name'] == 'Axion (6_3)':
        label_text = f"{row['name']}\n{row['mass']} MeV"
        ax.annotate(label_text, (row['metric'], row['mass']), 
                    xytext=(row['metric']+2, row['mass']*0.5),
                    arrowprops=dict(arrowstyle='->', color='red'),
                    fontsize=12, color='red', fontweight='bold')
    else:
        ax.text(row['metric']+0.2, row['mass']*0.8, row['name'], fontsize=10)

# 5. Styling
ax.set_yscale('log')
ax.set_xlabel('Topological Invariant (Volume / Complexity)', fontsize=12)
ax.set_ylabel('Mass [MeV]', fontsize=12)
ax.set_title('Figure 1: KSAU Mass Spectrum & Axion Prediction', fontsize=14, fontweight='bold')
ax.grid(True, which="both", ls="-", alpha=0.2)
ax.legend(loc='lower right')

ax.text(2.3, 3, r'$4_1$ (Down)', color='green', fontsize=9)
ax.text(5.5, 50, r'$6^3_2$ (Strange)', color='green', fontsize=9)
ax.text(14.5, 60000, r'W ($L11n387$)', color='purple', fontsize=9)

plt.tight_layout()
plt.savefig('v6.9/figures/figure_1_spectrum.png', dpi=300)
print("Figure 1 saved to v6.9/figures/figure_1_spectrum.png")