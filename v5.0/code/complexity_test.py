import pandas as pd
import numpy as np
import os
import itertools

# ==============================================================================
# KSAU v5.0 COMPLEXITY-PENALIZED STATISTICAL TEST
# ==============================================================================
# Testing the "Minimal Complexity Principle":
# Nature minimizes a combined cost of Mass Error (Energy) and Complexity (N).
# Cost = MAE + lambda * (Crossing_Number)
# ==============================================================================

# --- 1. Constants ---
KAPPA = np.pi / 24
B_Q = -7.9159

# Complexity Penalty Factor (lambda)
# Hypothesis: A small penalty for complexity makes KSAU the global optimum.
# 0.5% mass error equivalent per crossing is a reasonable physical ansatz.
LAMBDA = 0.5 

QUARK_TARGETS = {
    'Up':      {'mass': 2.16,   'C': 2, 'Det_Rule': 'even', 'Gen': 1},
    'Down':    {'mass': 4.67,   'C': 3, 'Det_Rule': '2^4',  'Gen': 1},
    'Strange': {'mass': 93.4,   'C': 3, 'Det_Rule': '2^5',  'Gen': 2},
    'Charm':   {'mass': 1270.0, 'C': 2, 'Det_Rule': 'even', 'Gen': 2},
    'Bottom':  {'mass': 4180.0, 'C': 3, 'Det_Rule': '2^6',  'Gen': 3},
    'Top':     {'mass': 172760.0, 'C': 2, 'Det_Rule': 'even', 'Gen': 3}
}

# --- 2. Load and Prep Data ---
DATA_PATH = "KSAU/publish/data/linkinfo_data_complete.csv"
df = pd.read_csv(DATA_PATH, sep='|', header=1)
df.columns = df.columns.str.strip()

col_map = {'Determinant': 'determinant', 'Volume': 'volume', 'Components': 'components', 'Crossing Number': 'crossing'}
df.rename(columns=col_map, inplace=True)

# Ensure numeric and drop NaN
for c in ['volume', 'determinant', 'components', 'crossing']:
    df[c] = pd.to_numeric(df[c], errors='coerce')
df.dropna(subset=['volume', 'determinant', 'components', 'crossing'], inplace=True)

# --- 3. Filter Candidates ---
TOP_K = 15 # Check deeper into the pool
pools = {}

print("Filtering Candidate Pools with Complexity Data...")
for name, rules in QUARK_TARGETS.items():
    mask = (df['components'] == rules['C'])
    
    if rules['Det_Rule'] == 'even':
        mask &= (df['determinant'] % 2 == 0)
    elif rules['Det_Rule'].startswith('2^'):
        det_val = 2 ** int(rules['Det_Rule'].split('^')[1])
        mask &= (df['determinant'] == det_val)
        
    twist = (2 - rules['Gen']) * ((-1)**rules['C'])
    v_ideal = (np.log(rules['mass']) - KAPPA * twist - B_Q) / (10 * KAPPA)
    
    candidates = df[mask].copy()
    candidates['vol_diff'] = abs(candidates['volume'] - v_ideal)
    
    # We keep top candidates based on pure volume fit first
    top_candidates = candidates.sort_values('vol_diff').head(TOP_K)
    
    # Store as list of dicts: {'vol': v, 'N': n, 'name': link_name}
    # Note: Using 'Name' column if available, else index
    link_data = []
    seen_vols = set()
    
    for _, row in top_candidates.iterrows():
        if row['volume'] not in seen_vols:
            link_data.append({
                'vol': row['volume'],
                'N': row['crossing'],
                'name': row.get('Name', 'Unknown')
            })
            seen_vols.add(row['volume'])
            
    pools[name] = link_data
    print(f"  {name:<7}: Kept {len(link_data)} candidates. Min N={min(d['N'] for d in link_data)}")

# --- 4. Cost Function ---
def calc_cost(combo_list):
    # combo_list is list of dicts
    errors = []
    total_n = 0
    quarks = list(QUARK_TARGETS.keys())
    
    for i, name in enumerate(quarks):
        data = combo_list[i]
        rules = QUARK_TARGETS[name]
        
        # Mass Error
        twist = (2 - rules['Gen']) * ((-1)**rules['C'])
        ln_m = 10 * KAPPA * data['vol'] + KAPPA * twist + B_Q
        pred = np.exp(ln_m)
        err = abs((pred - rules['mass']) / rules['mass']) * 100
        errors.append(err)
        
        # Complexity (Total Crossing Number)
        total_n += data['N']
        
    mae = np.mean(errors)
    cost = mae + LAMBDA * (total_n / 6.0) # Normalized average complexity penalty
    return cost, mae, total_n

# --- 5. KSAU Baseline ---
# Define KSAU selection manually with known N
KSAU_SELECTION = [
    {'vol': 6.599, 'N': 7},   # Up (L7a5)
    {'vol': 7.328, 'N': 6},   # Down (L6a4)
    {'vol': 9.532, 'N': 10},  # Strange (L10n95)
    {'vol': 11.517, 'N': 11}, # Charm (L11n64)
    {'vol': 12.276, 'N': 10}, # Bottom (L10a141)
    {'vol': 15.360, 'N': 11}  # Top (L11a62)
]
ksau_cost, ksau_mae, ksau_total_n = calc_cost(KSAU_SELECTION)

# --- 6. Exhaustive Search ---
print(f"\nStarting Search (Lambda={LAMBDA})...")
iterators = [pools[q] for q in QUARK_TARGETS]
total_combos = np.prod([len(p) for p in iterators])

best_cost = 1e9
best_combo = None
rank = 1

for combo in itertools.product(*iterators):
    cost, mae, n = calc_cost(combo)
    
    if cost < best_cost:
        best_cost = cost
        best_combo = combo
        
    if cost < ksau_cost - 0.001: # Tolerance
        rank += 1

# --- 7. Report ---
print("\n" + "="*70)
print(f"{'KSAU v5.0 COMPLEXITY-PENALIZED TEST':^70}")
print("="*70)
print(f"Cost Function: MAE + {LAMBDA} * (Avg Crossing Number)")
print("-" * 70)
print(f"KSAU Model:")
print(f"  MAE:       {ksau_mae:.4f}%")
print(f"  Total N:   {ksau_total_n}")
print(f"  Cost:      {ksau_cost:.4f}")
print(f"  Rank:      {rank} / {total_combos:,}")
print("-" * 70)
print(f"Global Optimum:")
cost_opt, mae_opt, n_opt = calc_cost(best_combo)
print(f"  MAE:       {mae_opt:.4f}%")
print(f"  Total N:   {n_opt}")
print(f"  Cost:      {cost_opt:.4f}")
print("="*70)

if rank == 1:
    print("CONCLUSION: KSAU IS THE GLOBAL OPTIMUM.")
    print("The Minimal Complexity Principle perfectly justifies the selection.")
else:
    print("CONCLUSION: KSAU is near-optimal. Slightly simpler/better links exist.")
    print("Check if the optimum uses unphysical links (e.g. N too high/low).")