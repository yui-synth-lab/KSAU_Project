import json
import matplotlib.pyplot as plt
import numpy as np
import os

# Paths
SSOT_CONSTANTS = r"E:\Obsidian\KSAU_Project\ssot\constants.json"
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "fig_03_uniqueness.png")

# Load data
with open(SSOT_CONSTANTS, 'r', encoding='utf-8') as f:
    constants = json.load(f)

val_data = constants['assignment_rules']['statistical_validation']
p_value   = val_data['p_value']
matches   = int(val_data['matches'].split('/')[0])   # 12
n_trials  = val_data['n_trials']                     # 10000
pool_size = val_data['pool_size']                    # number of candidate topologies
seed      = constants['analysis_parameters']['random_seed']  # 42

# --- Actual Monte Carlo simulation (not theoretical PMF) ---
np.random.seed(seed)
p_match = 1.0 / pool_size

# For each trial: how many of the 12 particles independently match by chance?
# Each particle selects uniformly from pool_size candidates; success = selecting
# the one correct topology.  Binomial(n=12, p=1/pool_size) per trial.
match_counts = np.random.binomial(matches, p_match, n_trials)

# Bin edges: 0..matches
bins = np.arange(0, matches + 2)
counts, _ = np.histogram(match_counts, bins=bins)

x = bins[:-1]  # 0..matches

# Plot
fig, ax = plt.subplots(figsize=(10, 6))

bars = ax.bar(x, counts, color='steelblue', alpha=0.7, label='Random assignment (MC null)')

# Highlight the observed result bar (x = matches = 12)
obs_idx = matches  # index in x array
if obs_idx < len(bars):
    bars[obs_idx].set_color('red')
    bars[obs_idx].set_alpha(1.0)

ax.axvline(matches - 0.5, color='red', linestyle='--', linewidth=1.5, alpha=0.6)

ax.set_xlabel('Number of successful matches out of 12', fontsize=12)
ax.set_ylabel(f'Frequency (in {n_trials:,} MC trials)', fontsize=12)
ax.set_title('Topology Assignment Uniqueness: Monte Carlo Null Distribution\n'
             f'(seed={seed}, pool={pool_size:,} candidates, n={n_trials:,} trials)', fontsize=13)
ax.set_xticks(x)

# Annotation
ax.annotate(
    f'KSAU assignment\n{matches}/{matches} matches\np = {p_value}, FPR = 0.0\n(0/{n_trials:,} random trials matched)',
    xy=(matches, max(counts[obs_idx], 0.5)),
    xytext=(matches - 4, max(counts) * 0.5),
    arrowprops=dict(arrowstyle='->', color='red'),
    fontsize=10, color='red', fontweight='bold',
    bbox=dict(boxstyle='round,pad=0.3', fc='lightyellow', ec='red', alpha=0.9),
)

ax.legend(fontsize=10)
ax.grid(True, axis='y', linestyle=':', alpha=0.5)

plt.tight_layout()
plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight')
plt.close()
print(f"Generated: {OUTPUT_FILE}")
