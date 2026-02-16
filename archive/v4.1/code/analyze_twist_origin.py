import pandas as pd
import numpy as np

# Load KnotInfo
try:
    df = pd.read_csv('data/knotinfo_data_complete.csv', sep='|', skiprows=[1], low_memory=False)
except:
    # Header handling fallback
    with open('data/knotinfo_data_complete.csv', 'r') as f:
        cols = f.readline().strip().split('|')
    df = pd.read_csv('data/knotinfo_data_complete.csv', sep='|', skiprows=2, names=cols, low_memory=False)

# Target Leptons
# 3_1 (Electron), 6_1 (Muon), 7_1 (Tau)
leptons = ['3_1', '6_1', '7_1']
target_df = df[df['name'].isin(leptons)].copy()

# Columns of interest (Topology)
cols_topo = [
    'name', 'crossing_number', 'determinant', 'signature', 
    'bridge_index', 'unknotting_number', 'arf_invariant', 
    'genus_3d', 'genus_4d', 'braid_index', 'symmetry_group',
    'hyperbolic_volume', 'chern_simons'
]

# Check if 'twist_number' or similar exists in columns
all_cols = [c.lower() for c in df.columns]
twist_cols = [c for c in df.columns if 'twist' in c.lower()]
print(f"Twist-related columns found: {twist_cols}")

# Extract data
print("\n--- Lepton Topological Invariants ---")
# Filter available columns
available_cols = [c for c in cols_topo if c in df.columns]
print(target_df[available_cols].to_string(index=False))

# Mathematical Analysis of -1/6
print("\n--- Search for -1/6 Origin ---")
# Muon(6_1) mass correction requires term -1/6 approx -0.1667
# Let's check ratios of invariants
for _, row in target_df.iterrows():
    name = row['name']
    try:
        det = float(row['determinant'])
        sig = float(row['signature'])
        n = float(row['crossing_number'])
        
        print(f"\n{name}:")
        print(f"  1/N = {1/n:.4f}")
        print(f"  1/Det = {1/det:.4f}")
        if sig != 0:
            print(f"  1/Sig = {1/sig:.4f}")
        else:
            print(f"  Sig = 0")
        print(f"  Sig/N = {sig/n:.4f}")
        print(f"  (N-Det)/N^2 = {(n-det)/(n**2):.4f}")
        
    except:
        pass