import pandas as pd
import numpy as np

def analyze_dark_matter_satellites():
    print("="*60)
    print("KSAU v6.4: Dark Matter (Satellite Shielding Analysis)")
    print("="*60)
    
    # 1. Load Data
    knots = pd.read_csv('data/knotinfo_data_complete.csv', sep='|', skiprows=[1])
    
    # 2. Identify Potential Satellites/Non-hyperbolic Knots
    knots['v'] = pd.to_numeric(knots['volume'], errors='coerce')
    non_hyperbolic = knots[(knots['v'].isna() | (knots['v'] == 0))].copy()
    non_hyperbolic['C'] = pd.to_numeric(non_hyperbolic['crossing_number'], errors='coerce')
    
    print(f"Total Non-hyperbolic/Satellite Candidates: {len(non_hyperbolic)}")
    
    # 3. Mass Estimation by Complexity (C)
    print("\n--- Potential High-Mass Dark Matter Candidates ---")
    print(f"{'Name':<12} | {'Crossing C':<12} | {'Structure'}")
    print("-" * 50)
    
    candidates = non_hyperbolic[non_hyperbolic['C'] >= 10].sort_values('C', ascending=False)
    for _, row in candidates.head(10).iterrows():
        name = row['name']
        c = row['C']
        print(f"{name:<12} | {c:<12.0f} | Satellite/Torus candidate")

    # 4. The Shielding Ratio
    print("\n[The Shielding Hypothesis]")
    # Example: A pattern knot (Visible) inside a companion torus (Dark).
    # The total volume (mass) is the sum of parts.
    v_pattern = 9.53  # e.g., Strange quark
    v_companion = 1.62 # e.g., A small torus companion (3_1 is 0, but topol. scale is small)
    
    # In KSAU scaling, Mass ~ exp(A*V)
    # A ~ 1.3
    A = 1.3085
    mass_visible = np.exp(A * v_pattern)
    mass_total = np.exp(A * (v_pattern + v_companion))
    
    ratio = mass_total / mass_visible
    print(f"  Visible Mass (exp(A*V_p)): {mass_visible:.2e}")
    print(f"  Total Mass with Companion: {mass_total:.2e}")
    print(f"  Dark/Visible Ratio: {ratio:.2f}")
    
    print("\nConclusion: If Dark Matter consists of 'nested' versions of standard particles,")
    print("the invisible companion torus provides the extra gravitational mass")
    print("without contributing to the gauge Linking Matrix.")

if __name__ == "__main__":
    analyze_dark_matter_satellites()