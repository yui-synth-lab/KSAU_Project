import pandas as pd
import numpy as np

# Load link info
try:
    df = pd.read_csv('data/linkinfo_data_complete.csv', sep='|', skiprows=[1], low_memory=False)
except Exception as e:
    print(f"Error loading CSV: {e}")
    # Try reading the first line to get columns
    with open('data/linkinfo_data_complete.csv', 'r') as f:
        cols = f.readline().strip().split('|')
    df = pd.read_csv('data/linkinfo_data_complete.csv', sep='|', skiprows=2, names=cols, low_memory=False)

# Clean numeric columns
def to_float(x):
    try:
        return float(x)
    except:
        return np.nan

df['volume'] = df['volume'].apply(to_float)
df['determinant'] = df['determinant'].apply(to_float)
df['components'] = df['components'].apply(to_float)

# Filter for relevant crossing numbers to keep it manageable
df = df[df['crossing_number'] <= 12]

targets = {
    'u': {'vol': 6.638, 'comp': 2},
    'd': {'vol': 7.234, 'comp': 3},
    's': {'vol': 9.516, 'comp': 3},
    'c': {'vol': 11.511, 'comp': 2},
    'b': {'vol': 12.423, 'comp': 3},
    't': {'vol': 15.267, 'comp': 2}
}

print(f"{'Quark':<6} {'Target V':>10} {'Comp':>5} {'Best Candidates'}")
print("-" * 60)

for quark, info in targets.items():
    # Filter by component count
    mask = (df['components'] == info['comp'])
    cands = df[mask].copy()
    
    # Calculate volume diff
    cands['vol_diff'] = np.abs(cands['volume'] - info['vol'])
    
    # Sort by vol_diff
    top_cands = cands.sort_values('vol_diff').head(5)
    
    cand_str = ""
    for _, row in top_cands.iterrows():
        cand_str += f"{row['name']} (V={row['volume']:.3f}, Det={row['determinant']:.0f}), "
    
    print(f"{quark:<6} {info['vol']:>10.3f} {info['comp']:>5.0f} {cand_str}")

# Check current ones specifically
current = {
    'u': 'L7a5',
    'd': 'L6a4',
    's': 'L10n95',
    'c': 'L11n64',
    'b': 'L10a141',
    't': 'L11a62'
}

print("\n\n" + "="*60)
print("  Current v4.0 Assignments Comparison")
print("="*60)
for quark, name in current.items():
    matches = df[df['name'].str.contains(name, na=False)]
    if not matches.empty:
        match = matches.iloc[0]
        vol = match['volume']
        det = match['determinant']
        target = targets[quark]['vol']
        diff = vol - target
        pct = (np.exp(1.3085 * vol - 7.9159) - np.exp(1.3085 * target - 7.9159)) / np.exp(1.3085 * target - 7.9159) * 100
        print(f"{quark:<2} {name:<10} V={vol:>7.3f} (Target {target:>7.3f}, Diff={diff:>+6.3f}) -> Error ~ {pct:>+5.1f}% | Det={det:.0f}")