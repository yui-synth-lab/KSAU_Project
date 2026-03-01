import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

SSOT_CONSTANTS = r"E:\Obsidian\KSAU_Project\ssot\constants.json"
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "fig_04_ckm_matrix.png")

with open(SSOT_CONSTANTS, 'r', encoding='utf-8') as f:
    constants = json.load(f)

v_obs = np.array(constants['ckm_matrix']['V_ij'])
r2    = constants['ckm_optimized_coefficients']['r2_achieved']  # 0.9980

# Error tiers from H67 ACCEPT verdict (cycle_26/verdict.md):
# Cabibbo-allowed diagonal: < 3% error
# Cabibbo-allowed off-diagonal: < 15% error
# Cabibbo-forbidden: 63-100% error
# Jarlskog J: 1.16% error
# CKM labels
rows = ['u', 'c', 't']
cols = ['d', 's', 'b']

# Category matrix: 0=CA-diag, 1=CA-off, 2=CF
# (Cabibbo-Allowed diagonal, CA-off-diagonal, Cabibbo-Forbidden)
# Diagonal (Vud, Vcs, Vtb) and near-diagonal (Vus, Vcd, Vcb, Vts) = CA
# Vub (u->b), Vtd (t->d) = most strongly suppressed (CF)
category = np.array([
    [0, 1, 2],  # u row: Vud(CA-diag), Vus(CA-off), Vub(CF)
    [1, 0, 1],  # c row: Vcd(CA-off), Vcs(CA-diag), Vcb(CA-off)
    [2, 1, 0],  # t row: Vtd(CF), Vts(CA-off), Vtb(CA-diag)
])

# Representative error % from H67 verdict (SSoT: ckm_matrix prediction_model)
err_labels = [
    ['~0.2%', '~7.6%', '~63%'],
    ['~7.6%', '~2.0%', '~1.2%'],
    ['~63%',  '~15%',  '~2.3%'],
]

fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# Left: Observed CKM matrix
im0 = axes[0].imshow(v_obs, cmap='viridis',
                     norm=plt.matplotlib.colors.LogNorm(vmin=0.003, vmax=1.0))
axes[0].set_title('Observed CKM Matrix $|V_{ij}|$', fontsize=13)
axes[0].set_xticks([0, 1, 2]); axes[0].set_xticklabels(cols, fontsize=12)
axes[0].set_yticks([0, 1, 2]); axes[0].set_yticklabels(rows, fontsize=12)
for i in range(3):
    for j in range(3):
        c = 'white' if v_obs[i, j] < 0.15 else 'black'
        axes[0].text(j, i, f'{v_obs[i,j]:.4f}', ha='center', va='center',
                     color=c, fontsize=11, fontweight='bold')

# Right: Error category heatmap
# Green = < 5%, Yellow = 5-20%, Red = > 20%
err_vals = np.array([
    [0.2,  7.6, 63.0],
    [7.6,  2.0,  1.2],
    [63.0, 15.0,  2.3],
])
cmap_err = plt.matplotlib.colors.LinearSegmentedColormap.from_list(
    'err', ['#2ca02c', '#f5a623', '#d62728'])
norm_err = plt.matplotlib.colors.LogNorm(vmin=0.1, vmax=100)

im1 = axes[1].imshow(err_vals, cmap=cmap_err, norm=norm_err)
axes[1].set_title(f'H67 Prediction Error (%) by CKM Element\n$R^2={r2}$, 5 free parameters',
                  fontsize=12)
axes[1].set_xticks([0, 1, 2]); axes[1].set_xticklabels(cols, fontsize=12)
axes[1].set_yticks([0, 1, 2]); axes[1].set_yticklabels(rows, fontsize=12)
for i in range(3):
    for j in range(3):
        txt_color = 'white' if err_vals[i, j] > 15 else 'black'
        axes[1].text(j, i, err_labels[i][j], ha='center', va='center',
                     color=txt_color, fontsize=11, fontweight='bold')

plt.colorbar(im1, ax=axes[1], label='Relative Error (%)')

# Legend for error categories
patches = [
    mpatches.Patch(color='#2ca02c', label='Cabibbo-allowed diagonal (<3%)'),
    mpatches.Patch(color='#f5a623', label='Cabibbo-allowed off-diag (<15%)'),
    mpatches.Patch(color='#d62728', label='Cabibbo-forbidden (63-100%)'),
]
axes[1].legend(handles=patches, loc='upper center',
               bbox_to_anchor=(0.5, -0.12), ncol=1, fontsize=9, framealpha=0.9)

plt.suptitle('CKM Matrix: Observed Values and H67 Geometric Model Errors',
             fontsize=14, y=1.01)
plt.tight_layout()
plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight')
plt.close()
print(f"Generated: {OUTPUT_FILE}")
