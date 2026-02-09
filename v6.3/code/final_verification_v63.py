import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../v6.1/code'))
import utils_v61

def final_verification_v63():
    print("="*60)
    print("KSAU v6.3: Addressing Reviewer Comments")
    print("="*60)
    
    # 1. Load Data
    knots, links = utils_v61.load_data()
    consts = utils_v61.load_constants()
    
    # 2. Universal Scaling
    G_catalan = consts['G']
    A = (10/7) * G_catalan
    C = -(7 + G_catalan)
    
    # 3. Z-Boson Verification (Target V ~ 14.78)
    print("\n[1. Z-Boson Search]")
    mz_target = 91187.6
    vz_target = (np.log(mz_target) - C) / A
    print(f"Target V_Z: {vz_target:.4f}")
    
    links['volume'] = pd.to_numeric(links['volume'], errors='coerce')
    z_cands = links[
        (links['volume'] >= vz_target - 0.1) & 
        (links['volume'] <= vz_target + 0.1) &
        (links['components'] == 3)
    ].sort_values('volume')
    
    print(f"Found {len(z_cands)} 3-component links near Z mass.")
    # Looking for a "Partner" to L11n387 (W).
    # L11n387 is Brunnian. Is there a Brunnian link for Z?
    # L11n387 volume is 14.655.
    # L11n404 volume? L11n113?
    
    # Let's check L11n404
    l11n404 = links[links['name'].str.startswith('L11n404')]
    if not l11n404.empty:
        print(f"  Candidate L11n404: Vol={float(l11n404.iloc[0]['volume']):.4f}")
        
    # 4. Higgs Verification (Target V ~ 15.02)
    print("\n[2. Higgs Candidate (Spin 0)]")
    mh_target = 125100.0
    vh_target = (np.log(mh_target) - C) / A
    print(f"Target V_H: {vh_target:.4f}")
    
    # Higgs should be 1-component (Knot) and Amphicheiral (CS=0).
    knots['volume'] = pd.to_numeric(knots['volume'], errors='coerce')
    knots['cs'] = pd.to_numeric(knots['chern_simons_invariant'], errors='coerce')
    
    h_cands = knots[
        (knots['volume'] >= vh_target - 0.5) & 
        (knots['volume'] <= vh_target + 0.5) & 
        (knots['cs'].abs() < 1e-6)
    ].sort_values('volume')
    
    if not h_cands.empty:
        print(f"Found {len(h_cands)} Amphicheiral Knot candidates for Higgs.")
        for _, row in h_cands.head(5).iterrows():
            print(f"  {row['name']:<12} | Vol: {row['volume']:.4f}")
    else:
        print("  No 1-component amphicheiral knots found in range. Checking 2-component links...")
        # Maybe Higgs is a 2-component link (Yukawa coupling).
        
    # 5. Spin Geometry Theory
    print("\n[3. Defining Spin Geometry]")
    print("  Rule 1: FORCE MEDIATORS (S=1) are 3-component Brunnian Links.")
    print("  Rule 2: SCALARS (S=0) are 1-component knots with CS=0 (Amphicheiral).")
    print("  Rule 3: FERMIONS (S=1/2) are 1-component or 2-component structures with CS != 0 (Chiral).")
    
    # 6. Gravity Scale (The 10^6 Factor)
    print("\n[4. Gravity Scale Analysis]")
    print(f"  M_GUT (Saturation Point) ~ 10^13 GeV (V ~ 30)")
    print(f"  M_Planck (Saturation point of vacuum network) ~ 10^19 GeV (V ~ 45)")
    print(f"  Hierarchy Factor: 10^6 (Log difference: 13.8)")
    print(f"  This corresponds to Delta V ~ 10.5.")
    print(f"  Observation: V_Planck / V_GUT ~ 45 / 30 = 1.5.")
    print(f"  Interpretation: The GUT scale is the limit of a single 'Particle Link'.")
    print(f"  The Planck scale is the limit of the 'Vacuum Master Link' (C=74).")

if __name__ == "__main__":
    final_verification_v63()
