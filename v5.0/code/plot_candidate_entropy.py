import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from pathlib import Path
import seaborn as sns

# ==============================================================================
# KSAU v5.0 Supplementary Figures Generator
# Generates Figure S1 (Top-10 Candidates) and Figure S2 (Entropy Heatmap)
#
# DATA SOURCE: Loads from topology_assignments.json
# ==============================================================================

# --- Constants ---
KAPPA = np.pi / 24
B_Q = -7.9159
B_L = -2.503

# --- Load particle data from JSON ---
def load_particle_data():
    json_path = Path(__file__).parent.parent / 'data' / 'topology_assignments.json'
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Select representative particles for entropy analysis
    particles = {}
    for name in ['Up', 'Down', 'Electron', 'Muon']:
        info = data[name]
        det_rule = 'even' if info['charge_type'] == 'up-type' else \
                   '2^4' if (info['charge_type'] == 'down-type' and info['generation'] == 1) else \
                   'odd'
        particles[name] = {
            'mass': info['observed_mass'],
            'C': info['components'],
            'Det_Rule': det_rule,
            'Gen': info['generation'],
            'Type': 'Quark' if info['charge_type'] != 'lepton' else 'Lepton'
        }
    return particles

PARTICLES = load_particle_data()

# --- Load Data ---
DATA_PATH = Path(__file__).parent.parent.parent / 'data' / 'linkinfo_data_complete.csv'
df = pd.read_csv(DATA_PATH, sep='|', header=1)
df.columns = df.columns.str.strip()
col_map = {'Determinant': 'determinant', 'Volume': 'volume', 'Components': 'components', 'Crossing Number': 'crossing'}
df.rename(columns=col_map, inplace=True)
for c in ['volume', 'determinant', 'components', 'crossing']:
    df[c] = pd.to_numeric(df[c], errors='coerce')
df.dropna(subset=['volume', 'determinant', 'components', 'crossing'], inplace=True)

# --- Analysis ---
def analyze_candidates():
    top_candidates_data = {}
    entropy_map = {}

    for name, rules in PARTICLES.items():
        # Filter
        mask = (df['components'] == rules['C'])
        if rules['Det_Rule'] == 'even':
            mask &= (df['determinant'] % 2 == 0)
        elif rules['Det_Rule'] == 'odd':
            mask &= (df['determinant'] % 2 != 0)
        elif rules['Det_Rule'].startswith('2^'):
            det_val = 2 ** int(rules['Det_Rule'].split('^')[1])
            mask &= (df['determinant'] == det_val)

        candidates = df[mask].copy()
        
        # Ideal Metric
        if rules['Type'] == 'Quark':
            twist = (2 - rules['Gen']) * ((-1)**rules['C'])
            v_ideal = (np.log(rules['mass']) - KAPPA * twist - B_Q) / (10 * KAPPA)
            candidates['diff'] = abs(candidates['volume'] - v_ideal)
        else:
            target_val = (np.log(rules['mass']) - B_L) / ((14/9)*KAPPA)
            if target_val < 0: target_val = 0
            n_ideal = np.sqrt(target_val)
            candidates['diff'] = abs(candidates['crossing'] - n_ideal)

        # Top 10
        top10 = candidates.sort_values('diff').head(10).copy()
        
        errors = []
        for _, row in top10.iterrows():
            if rules['Type'] == 'Quark':
                twist = (2 - rules['Gen']) * ((-1)**rules['C'])
                ln_m = 10*KAPPA*row['volume'] + KAPPA*twist + B_Q
                pred = np.exp(ln_m)
            else:
                ln_m = (14/9)*KAPPA*(row['crossing']**2) + B_L
                pred = np.exp(ln_m)
            err = abs((pred - rules['mass']) / rules['mass'])
            errors.append(err)
        
        top10['error'] = errors
        top_candidates_data[name] = top10
        
        # Entropy Calculation
        weights = np.exp(-np.array(errors))
        probs = weights / np.sum(weights)
        entropy_map[name] = -np.sum(probs * np.log(probs + 1e-10))

    return top_candidates_data, entropy_map

# --- Figure S1: Top 10 Candidates Relative Error ---
def plot_figure_s1(top_data):
    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # We plot Electron (Lepton) and Up (Quark) side by side
    particles_to_plot = ['Electron', 'Up']
    
    x_pos = []
    y_val = []
    colors = []
    labels = []
    
    idx_counter = 0
    for p_name in particles_to_plot:
        data = top_data[p_name].head(10)
        for i, (idx, row) in enumerate(data.iterrows()):
            x_pos.append(idx_counter)
            y_val.append(row['error'])
            colors.append('blue' if p_name=='Electron' else 'red')
            labels.append(f"{p_name} #{i+1}")
            idx_counter += 1
        idx_counter += 1 # Space between groups

    bars = ax.bar(x_pos, y_val, color=colors, alpha=0.7)
    
    # Axis formatting
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=10)
    ax.set_yscale('log') # Use log scale to show the massive difference
    ax.set_ylabel('Relative Mass Error (Log Scale)', fontsize=12)
    ax.set_title('Figure S1: Information Gap in Top-10 Candidates', fontsize=14)
    ax.grid(True, which="both", ls="-", alpha=0.2)
    
    # Legend
    from matplotlib.lines import Line2D
    custom_lines = [Line2D([0], [0], color='blue', lw=4),
                    Line2D([0], [0], color='red', lw=4)]
    ax.legend(custom_lines, ['Electron (Unique Solution)', 'Up Quark (Degenerate)'])

    plt.tight_layout()
    save_path = Path(__file__).parent.parent / 'figures' / 'figureS1_top10_errors.png'
    plt.savefig(save_path, dpi=300)
    print(f"Saved {save_path}")

# --- Figure S2: Entropy Heatmap ---
def plot_figure_s2(entropy_map):
    sns.set_style("white")
    fig, ax = plt.subplots(figsize=(8, 6))
    
    names = list(entropy_map.keys())
    vals = np.array(list(entropy_map.values()))
    
    # Reshape for heatmap (1 x 4)
    data_matrix = vals.reshape(1, -1)
    
    sns.heatmap(data_matrix, annot=True, cmap="Purples", 
                xticklabels=names, yticklabels=False,
                vmin=0, vmax=2.5, cbar_kws={'label': 'Selection Entropy (Nats)'}, ax=ax)
    
    ax.set_title('Figure S2: Topological Selection Entropy Heatmap', fontsize=14)
    ax.set_xlabel('Particle Species', fontsize=12)
    
    plt.tight_layout()
    save_path = Path(__file__).parent.parent / 'figures' / 'figureS2_entropy_heatmap.png'
    plt.savefig(save_path, dpi=300)
    print(f"Saved {save_path}")

if __name__ == "__main__":
    top, ent = analyze_candidates()
    plot_figure_s1(top)
    plot_figure_s2(ent)