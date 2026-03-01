import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../v6.1/code'))
import utils_v61

def search_bosons_and_spin():
    print("="*60)
    print("KSAU v6.3: Boson Identification & Spin Geometry")
    print("="*60)
    
    # 1. Load Data
    _, links = utils_v61.load_data()
    consts = utils_v61.load_constants()
    
    # 2. Define Mass Parameters
    kappa = consts['kappa']
    A = 10 * kappa
    C = -(7 + 7 * kappa)
    
    # 3. Target Boson Volumes
    # W: 80.377 GeV -> 14.681
    # Z: 91.187 GeV -> 14.777
    mw_mev = consts['bosons']['W']['observed_mass']
    mz_mev = consts['bosons']['Z']['observed_mass']
    mh_mev = consts['bosons']['Higgs']['observed_mass']
    
    vw_target = (np.log(mw_mev) - C) / A
    vz_target = (np.log(mz_mev) - C) / A
    vh_target = (np.log(mh_mev) - C) / A
    
    print(f"Target V_W: {vw_target:.4f}")
    print(f"Target V_Z: {vz_target:.4f}")
    print(f"Target V_H: {vh_target:.4f}")
    
    # 4. Search Criterion: Braid Index
    # Hypothesis: Spin S = (BraidIndex - 1) / 2
    # S=1/2 (Fermions) -> BraidIndex 2
    # S=1 (Gauge Bosons) -> BraidIndex 3
    # S=0 (Higgs) -> BraidIndex 1? No, 1 is Unknot.
    
    links['volume'] = pd.to_numeric(links['volume'], errors='coerce')
    links['braid_index'] = pd.to_numeric(links['braid_index'], errors='coerce')
    
    # Filter for Braid Index 3
    bosons = links[
        (links['braid_index'] == 3) & 
        (links['volume'] > 14.0) & 
        (links['volume'] < 16.0)
    ].copy()
    
    print("\n[Braid Index 3 Candidates (S=1)]")
    print(f"{'Name':<12} | {'Volume':<8} | {'Comp':<4} | {'Brunnian?'} | {'Diff W'} | {'Diff Z'}")
    print("-" * 80)
    
    import re
    for _, row in bosons.sort_values('volume').iterrows():
        vol = row['volume']
        comp = row.get('components', 'N/A')
        lm = str(row.get('linking_matrix', ''))
        nums = re.findall(r'-?\d+', lm)
        is_brunnian = all(n == '0' for n in nums) if nums else False
        
        diff_w = abs(vol - 14.681)
        diff_z = abs(vol - 14.777)
        
        if diff_w < 0.1 or diff_z < 0.1 or is_brunnian:
            br_str = "YES" if is_brunnian else "No"
            print(f"{row['name']:<12} | {vol:.4f}   | {comp:<4} | {br_str:<9} | {diff_w:.4f} | {diff_z:.4f}")

    # 5. Higgs Candidate (S=0)
    # If S=0 -> Braid Index 1? Unknot has V=0.
    # But Higgs has mass.
    # Maybe S=0 -> Braid Index 2 (like fermions) but Det=1? Or specific non-hyperbolic?
    # Or Higgs is a "Composite Link" of V ~ 15.0?
    
    # Let's search for Braid Index 2 links near V_H ~ 15.0
    higgs_cands = links[
        (links['braid_index'] == 2) & 
        (links['volume'] >= vh_target - 0.2) & 
        (links['volume'] <= vh_target + 0.2)
    ].sort_values('volume')
    
    print(f"\n[Higgs Candidates (Braid Index 2, V ~ {vh_target:.2f})]")
    for _, row in higgs_cands.head(5).iterrows():
        print(f"  {row['name']:<12} | Vol: {row['volume']:.4f}")

if __name__ == "__main__":
    search_bosons_and_spin()
