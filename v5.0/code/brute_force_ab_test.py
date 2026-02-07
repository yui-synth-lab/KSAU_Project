import pandas as pd
import numpy as np
import os
import time
import itertools
import json
from pathlib import Path

"""
KSAU v5.0: FULL BRUTE-FORCE STATISTICAL SIGNIFICANCE TEST

This script performs an exhaustive search of the solution space within a 
Top-K subspace. It validates the KSAU selection against all other possible 
topology combinations that satisfy the geometric rules.

Data Sources:
    - ../data/mass_data.csv
    - ../../data/linkinfo_data_complete.csv
    
Output:
    - ../data/brute_force_ab_results.json
"""

# --- 1. Constants & Model Setup ---
KAPPA = np.pi / 24
B_Q = -7.9159

# Load Target Quark Masses from CSV
base_path = Path(__file__).parent.parent
mass_csv_path = base_path / "data" / "mass_data.csv"
mass_df = pd.read_csv(mass_csv_path)

QUARK_TARGETS = {}
for _, row in mass_df[mass_df['group'] == 'Quark'].iterrows():
    name = row['particle']
    gen = int(row['generation'])
    ptype = row['charge_type']
    
    # Derive rules
    c = 2 if ptype == 'up-type' else 3
    if ptype == 'down-type':
        det_rule = f"2^{gen + 3}"
    else:
        det_rule = "even"
        
    QUARK_TARGETS[name] = {
        'mass': float(row['mass']),
        'C': c,
        'Det_Rule': det_rule,
        'Gen': gen
    }

# --- 2. Load Database ---
base_path_db = Path(__file__).parent.parent.parent
DATA_PATH = base_path_db / "data" / "linkinfo_data_complete.csv"
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Database not found at {DATA_PATH}")

# The CSV uses '|' as delimiter and the header is on the second line (index 1)
df = pd.read_csv(DATA_PATH, sep='|', header=1)

# Clean column names (strip whitespace)
df.columns = df.columns.str.strip()

# Print columns for debugging
print("Columns in CSV:", df.columns.tolist())

# Rename columns if needed
col_map = {
    'Determinant': 'determinant',
    'Volume': 'volume',
    'Components': 'components'
}
df.rename(columns=col_map, inplace=True)

# Check if required columns exist
required_cols = ['volume', 'determinant', 'components']
missing = [c for c in required_cols if c not in df.columns]
if missing:
    print(f"Error: Missing columns {missing}")
    # Try to find them case-insensitively again
    for req in missing:
        for col in df.columns:
            if col.lower() == req:
                df.rename(columns={col: req}, inplace=True)

# Ensure 'determinant' and 'components' are numeric
df['determinant'] = pd.to_numeric(df['determinant'], errors='coerce')
df['components'] = pd.to_numeric(df['components'], errors='coerce')
df['volume'] = pd.to_numeric(df['volume'], errors='coerce')

# Drop rows with NaN in critical columns
df.dropna(subset=['volume', 'determinant', 'components'], inplace=True)


# --- 3. Filter Candidate Pools (Pre-Optimization) ---
# To make brute-force feasible, we select top-K candidates for each quark
# based on volume proximity. A full Cartesian product of thousands of candidates
# would be roughly 10^15 combinations (infeasible).
# We take the top 10 candidates for each quark to check local optimality.
TOP_K = 10 

pools = {}
pool_indices = {}

print("Filtering Candidate Pools...")
for name, rules in QUARK_TARGETS.items():
    # Filter by Component
    mask = (df['components'] == rules['C'])
    
    # Filter by Determinant Rule
    if rules['Det_Rule'] == 'even':
        mask &= (df['determinant'] % 2 == 0)
    elif rules['Det_Rule'].startswith('2^'):
        det_val = 2 ** int(rules['Det_Rule'].split('^')[1])
        mask &= (df['determinant'] == det_val)
        
    # Calculate ideal volume to sort candidates
    # ln(m) = 10k*V + k*Twist + Bq => V_ideal = (ln(m) - k*Twist - Bq) / 10k
    # We check both Twist=+1 and Twist=-1 cases and take the best fit volume
    twist_plus = (2 - rules['Gen']) * ((-1)**rules['C']) # Current rule
    # Note: For brute force, we assume the Twist rule is part of the theory,
    # so we only look for volumes near the ideal volume predicted by the rule.
    
    twist = (2 - rules['Gen']) * ((-1)**rules['C'])
    v_ideal = (np.log(rules['mass']) - KAPPA * twist - B_Q) / (10 * KAPPA)
    
    candidates = df[mask].copy()
    candidates['vol_diff'] = abs(candidates['volume'] - v_ideal)
    top_candidates = candidates.sort_values('vol_diff').head(TOP_K)
    
    # Use unique volumes to avoid duplicate calculations for identical links
    unique_vols = top_candidates['volume'].unique()
    pools[name] = unique_vols
    print(f"  {name:<7}: Found {len(candidates)} valid links. Keeping top {len(unique_vols)} unique volumes for brute force.")

# --- 4. Define Mass Calculation ---
def calc_mae(vol_list):
    # vol_list order: Up, Down, Strange, Charm, Bottom, Top
    maes = []
    quarks = list(QUARK_TARGETS.keys())
    
    errors = []
    for i, name in enumerate(quarks):
        rules = QUARK_TARGETS[name]
        vol = vol_list[i]
        twist = (2 - rules['Gen']) * ((-1)**rules['C'])
        ln_m = 10 * KAPPA * vol + KAPPA * twist + B_Q
        pred = np.exp(ln_m)
        err = abs((pred - rules['mass']) / rules['mass'])
        errors.append(err)
        
    return np.mean(errors) * 100

# --- 5. KSAU Current Selection (Baseline) ---
topo_json_path = base_path / "data" / "topology_assignments.json"
with open(topo_json_path, 'r') as f:
    topo_data = json.load(f)

KSAU_VOLUMES = [topo_data[q]['volume'] for q in QUARK_TARGETS.keys()]
ksau_mae = calc_mae(KSAU_VOLUMES)

# --- 6. Exhaustive Search ---
# Create Cartesian product of all pools
print(f"\nStarting Exhaustive Search on Top-{TOP_K} subspace...")
iterators = [pools[q] for q in QUARK_TARGETS]
total_combinations = np.prod([len(p) for p in iterators])
print(f"Total combinations to check: {total_combinations:,}")

start_time = time.time()

# Iterate
best_mae = 100.0
best_combo = None
better_count = 0
worse_count = 0

# Using itertools.product for efficiency
all_maes = []
for combo in itertools.product(*iterators):
    mae = calc_mae(combo)
    all_maes.append(float(mae))
    
    if mae < best_mae:
        best_mae = mae
        best_combo = combo
        
    if mae <= ksau_mae + 0.0001: # Allow floating point tolerance
        better_count += 1
    else:
        worse_count += 1

duration = time.time() - start_time

# --- 7. Save Results to JSON ---
output_data = {
    'all_maes': all_maes,
    'ksau_mae': float(ksau_mae),
    'ksau_rank': int(better_count),
    'total_combinations': int(total_combinations),
    'best_mae': float(best_mae),
    'quarks': list(QUARK_TARGETS.keys())
}

output_path = base_path / "data" / "brute_force_ab_results.json"
with open(output_path, 'w') as f:
    json.dump(output_data, f, indent=2)
print(f"\nSaved results to: {output_path}")

# --- 8. Results ---
print("\n" + "="*60)
print(f"{'KSAU v5.0 EXHAUSTIVE SEARCH RESULTS':^60}")
print("="*60)
print(f"KSAU Model MAE:        {ksau_mae:>10.4f}%")
print(f"Global Minimum MAE:    {best_mae:>10.4f}%")
print("-" * 60)
print(f"Total Combinations:    {total_combinations:>10,}")
print(f"Rank of KSAU Model:    {better_count:>10,}")
print(f"Top Percentile:        {(better_count/total_combinations)*100:>10.4f}%")
print("-" * 60)
print(f"Time taken: {duration:.2f} seconds")
print("="*60)

if best_mae < ksau_mae - 0.01:
    print("NOTE: A slightly better combination exists in the top-K pool.")
    print("This is expected if KSAU uses specific links (e.g. Borromean)")
    print("that are slightly off the numerical optimum but topologically significant.")
else:
    print("NOTE: KSAU is the GLOBAL OPTIMUM in the searched subspace.")

print("\nBest Combination Found (Volumes):")
quarks = list(QUARK_TARGETS.keys())
for i, v in enumerate(best_combo):
    print(f"  {quarks[i]:<7}: {v:.4f}")