import pandas as pd
import numpy as np
import re

# Load Data
try:
    df = pd.read_csv('data/linkinfo_data_complete.csv', sep='|', skiprows=[1], low_memory=False)
except:
    with open('data/linkinfo_data_complete.csv', 'r') as f:
        cols = f.readline().strip().split('|')
    df = pd.read_csv('data/linkinfo_data_complete.csv', sep='|', skiprows=2, names=cols, low_memory=False)

# Numeric conversions
df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
df['determinant'] = pd.to_numeric(df['determinant'], errors='coerce')

# Candidates
top_cands = ['L11a144', 'L11a329']
print("--- Top Quark Candidate Analysis ---")

for cand in top_cands:
    matches = df[df['name'].str.contains(cand, na=False)]
    if not matches.empty:
        print(f"\n[{cand}] Variants found: {len(matches)}")
        cols = ['name', 'volume', 'determinant', 'signature', 'linking_matrix', 'symmetry_group']
        # Check if columns exist
        use_cols = [c for c in cols if c in df.columns]
        print(matches[use_cols].to_string(index=False))
        
        # Calculate Linking Number Sum if matrix exists
        if 'linking_matrix' in df.columns:
            for _, row in matches.iterrows():
                try:
                    mat_str = row['linking_matrix']
                    # Simple parse
                    nums = [int(x) for x in re.findall(r'-?\d+', mat_str)]
                    l_tot = sum([abs(x) for x in nums]) // 2
                    print(f"  {row['name']} -> Total Linking Number (abs): {l_tot}")
                except:
                    pass
    else:
        print(f"\n[{cand}] No matches found.")