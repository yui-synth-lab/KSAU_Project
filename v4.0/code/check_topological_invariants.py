
import pandas as pd
import numpy as np
import os
import sys

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "..", "data", "linkinfo_data_complete.csv")

# KSAU v4.0 Assignments
ASSIGNMENTS = {
    'u': 'L7a5',
    'd': 'L6a4',
    's': 'L10n95', # The new v3.4/4.0 candidate
    'c': 'L11n64',
    'b': 'L10a141',
    't': 'L11a62'
}

# Competitors (Volume neighbors but rejected)
COMPETITORS = {
    's_rival': 'L11n419', # Strange rival
    'b_rival': 'L10a146', # Bottom rival (better volume fit but rejected)
    't_rival': 'L10a107'  # Top rival
}

def load_data():
    print(f"Loading data from {DATA_PATH}...")
    # Read only necessary columns to save memory if needed, but here we read all to inspect
    df = pd.read_csv(DATA_PATH, sep='|', low_memory=False, skiprows=[1])
    return df

def extract_invariants(df, target_names):
    # Filter for targets
    # Note: Names in CSV might have orientation suffix like {0}, {1} etc.
    # We take the first match for simplicity or all matches.
    
    results = []
    
    for label, base_name in target_names.items():
        # Search for exact match or starts with
        mask = df['name'] == base_name
        if not mask.any():
             mask = df['name'].str.startswith(base_name + '{')
        
        matches = df[mask]
        
        if len(matches) == 0:
            print(f"Warning: {base_name} ({label}) not found.")
            continue
            
        # Take the first variation (usually {0} or {0,0})
        # Ideally we should check if invariants vary across orientations.
        # Volume is constant, but Jones/Signature might change sign or value.
        row = matches.iloc[0]
        
        info = {
            'label': label,
            'name': row['name'],
            'vol': float(row['volume']),
            'comp': int(row['components']),
            'sign': row.get('signature', 'N/A'),
            'det': row.get('determinant', 'N/A'),
            'jones': row.get('jones_polynomial', 'N/A'),
            'homfly': row.get('homflypt_polynomial', 'N/A'),
            'alex': row.get('multivariable_alexander', 'N/A'),
            'braid': row.get('braid_notation', 'N/A'),
            'linking': row.get('linking_matrix', 'N/A')
        }
        results.append(info)
        
    return pd.DataFrame(results)

def main():
    df = load_data()
    
    # 1. Analyze Selected Quarks
    print("\n--- KSAU v4.0 Selected Quarks ---")
    df_selected = extract_invariants(df, ASSIGNMENTS)
    print(df_selected[['label', 'name', 'vol', 'sign', 'det']].to_string(index=False))
    
    # 2. Analyze Competitors
    print("\n--- Competitors (Rejected) ---")
    df_rivals = extract_invariants(df, COMPETITORS)
    print(df_rivals[['label', 'name', 'vol', 'sign', 'det']].to_string(index=False))
    
    # 3. Deep Dive Comparison: Strange (L10n95 vs L11n419)
    print("\n--- Deep Dive: Strange Quark Selection ---")
    s_row = df_selected[df_selected['label'] == 's'].iloc[0]
    r_row = df_rivals[df_rivals['label'] == 's_rival'].iloc[0]
    
    print(f"Feature      | Selected (L10n95) | Rival (L11n419)")
    print(f"-------------|-------------------|----------------")
    print(f"Volume       | {s_row['vol']:<17} | {r_row['vol']}")
    print(f"Components   | {s_row['comp']:<17} | {r_row['comp']}")
    print(f"Signature    | {s_row['sign']:<17} | {r_row['sign']}")
    print(f"Determinant  | {s_row['det']:<17} | {r_row['det']}")
    print(f"Linking Mat  | {str(s_row['linking'])[:17]} | {str(r_row['linking'])[:15]}...")
    
    # Check Jones Polynomial (Text based)
    print(f"Jones Poly   | {str(s_row['jones'])[:30]}... | {str(r_row['jones'])[:30]}...")

if __name__ == "__main__":
    main()
