
import pandas as pd
import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOT_DATA = os.path.join(BASE_DIR, "..", "..", "data", "knotinfo_data_complete.csv")

def scan_knot_candidates():
    print(f"Scanning KnotInfo for Lepton Candidates (N=3, 6, 7)...")
    
    # Target Crossing Numbers
    targets = [3, 6, 7]
    candidates = []

    # Read in chunks to handle large file
    chunksize = 1000
    try:
        # Note: Separator might be different or standard CSV. Usually KnotInfo is CSV or Excel.
        # Assuming standard CSV based on extension, but linkinfo was '|'. Let's try ',' first then '|'.
        # The user file list showed .csv, previous read_file of linkinfo worked with '|'.
        # Let's peek at the file format first implicitly by trying '|' which is safer for these datasets.
        
        for chunk in pd.read_csv(KNOT_DATA, sep='|', chunksize=chunksize, low_memory=False, skiprows=[1]):
            # Filter by crossing number
            # Column name might be 'crossing_number' or similar.
            if 'crossing_number' not in chunk.columns:
                continue
                
            mask = chunk['crossing_number'].isin(targets)
            if mask.any():
                matches = chunk[mask]
                for _, row in matches.iterrows():
                    candidates.append({
                        'name': row['name'],
                        'N': row['crossing_number'],
                        'det': row.get('determinant', 'N/A'),
                        'sign': row.get('signature', 'N/A'),
                        'vol': row.get('volume', 'N/A'),
                        'alex': str(row.get('multivariable_alexander', 'N/A'))[:20],
                        'jones': str(row.get('jones_polynomial', 'N/A'))[:20]
                    })
    except Exception as e:
        print(f"Error reading KnotInfo: {e}")
        return

    # Convert to DataFrame
    df = pd.DataFrame(candidates)
    
    # Sort
    df['N'] = pd.to_numeric(df['N'])
    df = df.sort_values(by=['N', 'name'])
    
    # Display Results
    print("\n--- Electron Candidates (N=3) ---")
    print(df[df['N'] == 3][['name', 'det', 'sign', 'vol']].to_string(index=False))

    print("\n--- Muon Candidates (N=6) ---")
    print(df[df['N'] == 6][['name', 'det', 'sign', 'vol']].to_string(index=False))

    print("\n--- Tau Candidates (N=7) ---")
    # Show only torus-like or simple ones to save space? No, show all 7s (there are 7 of them: 7_1 to 7_7)
    print(df[df['N'] == 7][['name', 'det', 'sign', 'vol']].to_string(index=False))

def analyze_up_determinants():
    # Hardcoded from previous check for u, c, t
    # u (L7a5): 18
    # c (L11n64): 12
    # t (L11a62): 124
    
    dets = {'u': 18, 'c': 12, 't': 124}
    print("\n--- Up-Type Quark Determinant Analysis ---")
    for q, d in dets.items():
        print(f"{q.upper()}: {d}")
        # Factorize
        if d % 2 == 0:
            print(f"  -> 2 * {d//2}")
        if d % 4 == 0:
            print(f"  -> 4 * {d//4}")
            
    print("\nHypothesis Check:")
    print("All are Even? Yes.")
    print("All are 4k? u(18) is not 4k (18=4*4+2).")
    print("Rule: Det = 2 * (Odd Number)?")
    print(f"u: 18 = 2 * 9 (Odd)")
    print(f"c: 12 = 2 * 6 (Even) -> No.")
    print(f"t: 124 = 2 * 62 (Even) -> No.")
    
    print("Rule: Det = 4k + 2 ?")
    print(f"u: 18 = 4*4 + 2 (Yes)")
    print(f"c: 12 = 4*3 + 0 (No)")
    print(f"t: 124 = 4*31 + 0 (No)")
    
    print("Conclusion: Up-type pattern is complex or requires larger dataset.")

if __name__ == "__main__":
    scan_knot_candidates()
    analyze_up_determinants()
