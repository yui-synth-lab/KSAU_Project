import numpy as np
import pandas as pd
import utils_v61

def calc_dm_cross_section():
    print("="*60)
    print("KSAU v6.1: Dark Matter (Shadow Topology) Cross-Section")
    print("="*60)
    
    # 1. Target Candidate
    name = "12n_430"
    print(f"Target Candidate: {name}")
    
    # 2. Get Data
    knots, _ = utils_v61.load_data()
    row = knots[knots['name'] == name].iloc[0]
    
    vol = float(row['volume'])
    crossing = int(row['crossing_number'])
    
    # Check if 'average_crossing_number' exists, else use crossing_number
    # The dataframe might not have it loaded or it's named differently.
    # We'll use crossing_number as proxy for "Shadow Complexity".
    
    print(f"  Volume: {vol:.4f}")
    print(f"  Crossing Number (Shadow Proxy): {crossing}")
    
    # 3. Calculate Cross-Section
    # Baseline: Weak Scale ~ 10^-38 cm2 (pb)
    # Suppression: exp( - Shadow_Factor ) ?
    # Let's assume Shadow Factor = Crossing Number.
    # Sigma = Sigma_weak * exp( - Crossing ) ?
    # e^-12 ~ 6e-6.
    # 10^-38 * 6e-6 ~ 10^-44 cm2.
    # LZ limit for 1-10 GeV is around 10^-46 cm2 or lower.
    
    # Let's use a "Geometric Shadow" formula from Paper III (Hypothetical):
    # Sigma = Sigma_0 * (1 / Det^2) * exp( - V ) ? Det=1.
    # Sigma = Sigma_0 * exp( - 2 * V ) ?
    # Sigma_0 ~ 10^-40 cm2 (Neutrino-like?)
    
    # Let's define the "Shadow Suppression" S.
    # S = exp(- Volume * Crossing / 10) ?
    
    sigma_weak = 1e-38 # cm2
    
    # Model 1: Volume Suppression
    # Sigma = Sigma_weak * exp(-V)
    sigma_1 = sigma_weak * np.exp(-vol)
    
    # Model 2: Crossing Suppression (Shadow)
    # Sigma = Sigma_weak * exp(-Crossing)
    sigma_2 = sigma_weak * np.exp(-crossing)
    
    # Model 3: Combined
    # Sigma = Sigma_weak * exp(-V - Crossing/2)
    sigma_3 = sigma_weak * np.exp(-vol - crossing/2)
    
    print("\n[Cross-Section Estimates]")
    print(f"Baseline (Weak): {sigma_weak:.1e} cm^2")
    print(f"Model 1 (Vol Only): {sigma_1:.1e} cm^2 (LZ Limit ~ 1e-46)")
    print(f"Model 2 (Shadow Only): {sigma_2:.1e} cm^2")
    print(f"Model 3 (Combined): {sigma_3:.1e} cm^2")
    
    limit_lz = 1e-46
    print(f"\nLZ Limit (approx): {limit_lz:.1e} cm^2")
    
    print("\nVerification:")
    if sigma_3 < limit_lz:
        print("  PASS: Predicted cross-section is below detection limits.")
    else:
        print("  FAIL: Predicted cross-section is visible (or excluded).")
        print(f"  Exclusion Factor: {sigma_3 / limit_lz:.1f}x too large.")
        
    # Additional: 12n_242 (Warm DM)
    print("\n[Warm DM Check: 12n_242]")
    row2 = knots[knots['name'] == '12n_242'].iloc[0]
    v2 = float(row2['volume'])
    c2 = int(row2['crossing_number'])
    s_warm = sigma_weak * np.exp(-v2 - c2/2)
    print(f"  Sigma: {s_warm:.1e} cm^2")

if __name__ == "__main__":
    calc_dm_cross_section()
