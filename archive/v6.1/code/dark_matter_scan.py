import pandas as pd
import numpy as np
import utils_v61

def run_dark_matter_scan():
    print("="*60)
    print("KSAU v6.1: Dark Matter (Det=1) Candidate Scan")
    print("="*60)
    
    # 1. Load Knots
    knots, _ = utils_v61.load_data()
    
    # 2. Filter Det=1 and Volume > 0
    # Determinant is in 'determinant' column.
    # Volume is in 'volume' column.
    
    # Ensure numeric
    knots['determinant'] = pd.to_numeric(knots['determinant'], errors='coerce')
    knots['volume'] = pd.to_numeric(knots['volume'], errors='coerce')
    
    candidates = knots[
        (knots['determinant'] == 1) & 
        (knots['volume'] > 0)
    ].copy()
    
    print(f"Found {len(candidates)} Det=1 Hyperbolic Knots.")
    
    # 3. Calculate Mass
    # Formula from physical theory (Upgrade Log): ln(m) = (10/7 * G) * V - (7 + G)
    # where G = Catalan's constant
    consts = utils_v61.load_constants()
    G_catalan = consts['G_catalan']

    # Use Catalan-based formula (matches Upgrade Log documentation)
    slope = (10.0 / 7.0) * G_catalan  # ~ 1.3085
    intercept = -(7.0 + G_catalan)    # ~ -7.9160

    # Note: Alternative formulation uses kappa = G_catalan / 7 ≈ 0.1309
    # Both are numerically equivalent but Catalan-based is more fundamental
    
    candidates['predicted_mass_MeV'] = np.exp(slope * candidates['volume'] + intercept)
    candidates['predicted_mass_keV'] = candidates['predicted_mass_MeV'] * 1000
    candidates['predicted_mass_GeV'] = candidates['predicted_mass_MeV'] / 1000
    
    # 4. Search for Warm DM (10-20 keV)
    warm_dm = candidates[
        (candidates['predicted_mass_keV'] >= 10) & 
        (candidates['predicted_mass_keV'] <= 25)
    ].sort_values('predicted_mass_keV')
    
    print("\n[Warm Dark Matter Candidates (10-25 keV)]")
    print(f"{'Name':<12} | {'Volume':<8} | {'Mass (keV)':<10} | {'Poly'}")
    for _, row in warm_dm.head(10).iterrows():
        print(f"{row['name']:<12} | {row['volume']:.4f}   | {row['predicted_mass_keV']:.2f}       | {str(row['jones_polynomial'])[:20]}...")
        
    # 5. Search for WIMP (1-10 GeV)
    wimp = candidates[
        (candidates['predicted_mass_GeV'] >= 1) & 
        (candidates['predicted_mass_GeV'] <= 10)
    ].sort_values('predicted_mass_GeV')
    
    print("\n[WIMP Candidates (1-10 GeV)]")
    print(f"{'Name':<12} | {'Volume':<8} | {'Mass (GeV)':<10} | {'Poly'}")
    for _, row in wimp.head(10).iterrows():
        print(f"{row['name']:<12} | {row['volume']:.4f}   | {row['predicted_mass_GeV']:.2f}       | {str(row['jones_polynomial'])[:20]}...")

if __name__ == "__main__":
    run_dark_matter_scan()
