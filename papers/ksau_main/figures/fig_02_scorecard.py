import json
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import os

STATUS_FILE = r"E:\Obsidian\KSAU_Project\ssot\project_status.json"
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "fig_02_scorecard.png")

with open(STATUS_FILE, 'r', encoding='utf-8') as f:
    status = json.load(f)

hypotheses = status['hypotheses_index']

cycles = sorted(set(h['cycle'] for h in hypotheses))
h_nums = sorted(int(h['id'].strip('"')[1:]) for h in hypotheses)

col_min, col_max = min(cycles), max(cycles)
row_min, row_max = min(h_nums), max(h_nums)

# Discrete encoding: 0=empty, 1=ACCEPT, 2=REJECT, 3=MODIFIED
matrix = np.zeros((row_max - row_min + 1, col_max - col_min + 1), dtype=float)
for h in hypotheses:
    hnum = int(h['id'].strip('"')[1:])
    cyc  = h['cycle']
    s    = h['status']
    r = hnum - row_min
    c = cyc  - col_min
    if   s == 'accepted': matrix[r, c] = 1.0
    elif s == 'rejected': matrix[r, c] = 2.0
    elif s == 'modified': matrix[r, c] = 3.0

# White / green / red / gold  (color-blind safe: distinguishable by both hue and lightness)
cmap = mcolors.ListedColormap(['#f0f0f0', '#2ca02c', '#d62728', '#e8a020'])
norm = mcolors.BoundaryNorm([0, 0.5, 1.5, 2.5, 3.5], cmap.N)

fig, ax = plt.subplots(figsize=(14, 10))
ax.imshow(matrix, aspect='auto', cmap=cmap, norm=norm, origin='lower',
          extent=[col_min - 0.5, col_max + 0.5, row_min - 0.5, row_max + 0.5])

# Manual legend patches
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#2ca02c', label='ACCEPTED (41)'),
    Patch(facecolor='#d62728', label='REJECTED (24)'),
    Patch(facecolor='#e8a020', label='MODIFIED (4)'),
    Patch(facecolor='#f0f0f0', edgecolor='gray', label='Not tested'),
]
ax.legend(handles=legend_elements, loc='upper left', fontsize=10, framealpha=0.9)

ax.set_xlabel('Cycle Number', fontsize=12)
ax.set_ylabel('Hypothesis ID (H#)', fontsize=12)
ax.set_title('Hypothesis Test Scorecard: 69 Tests across 26 AIRDP Cycles', fontsize=13)
ax.set_xticks(range(col_min, col_max + 1))
ax.set_xticklabels(range(col_min, col_max + 1), fontsize=8)
ax.tick_params(axis='y', labelsize=8)

plt.tight_layout()
plt.savefig(OUTPUT_FILE, dpi=300)
plt.close()
print(f"Generated: {OUTPUT_FILE}")
