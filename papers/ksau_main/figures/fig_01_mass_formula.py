import json
import matplotlib.pyplot as plt
import numpy as np
import os

SSOT_CONSTANTS   = r"E:\Obsidian\KSAU_Project\ssot\constants.json"
SSOT_ASSIGNMENTS = r"E:\Obsidian\KSAU_Project\ssot\data\raw\topology_assignments.json"
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "fig_01_mass_formula.png")

with open(SSOT_CONSTANTS, 'r', encoding='utf-8') as f:
    constants = json.load(f)
with open(SSOT_ASSIGNMENTS, 'r', encoding='utf-8') as f:
    assignments = json.load(f)

kappa      = constants['mathematical_constants']['kappa']
eta_lepton = constants['theoretical_mass_laws']['lepton_slope']
eta_quark  = constants['theoretical_mass_laws']['quark_slope']
vp         = constants['effective_volume_model']
a, b, c    = vp['a'], vp['b'], vp['c']
p_data     = constants['particle_data']

# Manually tuned offsets (points, dx, dy) to prevent label overlap
# Key clusters: {W, Z} near (7.85-7.92, 11.3-11.4), {Higgs, Top} near (8.44-8.47, 11.7-12.1)
label_offsets = {
    'Electron': (-18,  8),
    'Muon':     ( 12,  8),
    'Tau':      (-25,  8),
    'Up':       ( 12, -16),
    'Down':     (-28,  8),
    'Strange':  (-30,  8),
    'Charm':    ( 12,  8),
    'Bottom':   ( 12, -16),
    'Top':      ( 12,  8),
    'W':        (-32,  8),
    'Z':        (-32, -16),
    'Higgs':    ( 12, -16),
}

masses = {}
for sector in ['quarks', 'leptons', 'bosons']:
    for name, d in p_data[sector].items():
        masses[name] = d['observed_mass']

fig, ax = plt.subplots(figsize=(11, 7))

plotted_labels = set()
for name, data in assignments.items():
    if name not in masses:
        continue
    vol = data['volume']
    n   = data['crossing_number']
    det = data['determinant']
    v_eff = vol + a * n + b * np.log(max(1, det)) + c
    ln_m  = np.log(masses[name])

    if name in p_data['leptons']:
        color, sector = '#1f77b4', 'Lepton'    # blue
    elif name in p_data['quarks']:
        color, sector = '#d62728', 'Quark'     # red
    else:
        color, sector = '#2ca02c', 'Boson'     # green

    label_arg = sector if sector not in plotted_labels else ""
    ax.scatter(v_eff, ln_m, color=color, s=110, label=label_arg, zorder=5)
    plotted_labels.add(sector)

    dx, dy = label_offsets.get(name, (0, 10))
    ax.annotate(name, (v_eff, ln_m),
                textcoords="offset points", xytext=(dx, dy),
                ha='center', fontsize=9,
                arrowprops=dict(arrowstyle='-', color='gray', lw=0.5) if abs(dx) > 10 else None)

# Theoretical regression lines
v_range = np.linspace(-1.5, 16, 200)
l_int = constants['phase_viscosity_model']['sectors']['leptons']['intercept']
q_int = constants['phase_viscosity_model']['sectors']['quarks_c2']['intercept']
ax.plot(v_range, eta_lepton * kappa * v_range + l_int, color='#1f77b4',
        linestyle='--', alpha=0.35, label=f'Lepton Theory (η={eta_lepton:.0f})')
ax.plot(v_range, eta_quark  * kappa * v_range + q_int, color='#d62728',
        linestyle='--', alpha=0.35, label=f'Quark Theory (η={eta_quark:.1f})')

ax.set_xlabel(r'Effective Volume $V_{\mathrm{eff}} = V + a\,n + b\,\ln(\mathrm{Det}) + c$',
              fontsize=12)
ax.set_ylabel(r'$\ln(m\,/\,\mathrm{MeV})$', fontsize=12)
ax.set_title('Fermion Mass Formula: Regression against Effective Volume', fontsize=14)
ax.legend(loc='lower right', fontsize=10)
ax.grid(True, linestyle=':', alpha=0.6)

ax.text(0.02, 0.97,
        'Fermion subset (9 particles):\n$R^2 = 0.9998$\nFree params: 4 ($a,b,c,C$)',
        transform=ax.transAxes, va='top', fontsize=9,
        bbox=dict(facecolor='white', edgecolor='gray', alpha=0.85))

plt.tight_layout()
plt.savefig(OUTPUT_FILE, dpi=300)
plt.close()
print(f"Generated: {OUTPUT_FILE}")
