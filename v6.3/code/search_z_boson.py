import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../v6.1/code'))
import utils_v61

def search_z_boson_brunnian():
    print("="*60)
    print("KSAU v6.3: Z-Boson Brunnian Identification")
    print("="*60)
    
    # 1. Load Data & Constants
    _, links = utils_v61.load_data()
    consts = utils_v61.load_constants()
    
    # 2. Calculate Target Volume V_Z
    G_catalan = consts['G']
    A = (10/7) * G_catalan
    C = -(7 + G_catalan)
    
    # Z Boson Mass (Experimental)
    mz_mev = 91187.6
    target_vol = (np.log(mz_mev) - C) / A
    print(f"Target Volume for M_Z ({mz_mev} MeV): {target_vol:.4f}")
    
    # 3. Filter for candidates
    # Z is neutral, so maybe Det=1 or specific symmetry.
    # It must be a 'clasp' like W, so 3-components and Brunnian.
    
    links['volume'] = pd.to_numeric(links['volume'], errors='coerce')
    
    candidates = links[
        (links['volume'] >= target_vol - 0.2) & 
        (links['volume'] <= target_vol + 0.2) &
        (links['components'] == 3)
    ].copy()
    
    print(f"Found {len(candidates)} 3-component links in range.")
    
    print("\n[Candidates for Z-Boson]")
    print(f"{'Name':<12} | {'Volume':<8} | {'Brunnian?'} | {'Diff'}")
    print("-" * 50)
    
    import re
    for _, row in candidates.sort_values('volume').iterrows():
        vol = row['volume']
        diff = abs(vol - target_vol)
        
        # Brunnian check (Linking Matrix == 0)
        lm = str(row.get('linking_matrix', ''))
        nums = re.findall(r'-?\d+', lm)
        is_brunnian = all(n == '0' for n in nums) if nums else False
        
        if is_brunnian or diff < 0.05:
            br_str = "YES" if is_brunnian else "No"
            print(f"{row['name']:<12} | {vol:.4f}   | {br_str:<9} | {diff:.4f}")

    # 4. Hypothesis: The Z-W mass ratio is geometric
    # rho = Mw / (Mz * cos_theta_w) ~ 1
    # Mw^2 / Mz^2 = cos^2_theta_w
    # exp(2*A*Vw) / exp(2*A*Vz) = cos^2
    # exp(2*A*(Vw-Vz)) = cos^2
    
    print("\n[Electroweak Rho Parameter Check]")
    vw = 14.6554 # L11n387
    vz_cand = 14.7777 # Target
    
    cos2_theta_w = 1.0 - 0.23122 # Standard value
    pred_ratio_vol = np.exp(2 * A * (vw - target_vol))
    
    print(f"  Observed cos^2(theta_W): {cos2_theta_w:.4f}")
    print(f"  Geometric Predicted ratio: {pred_ratio_vol:.4f}")
    print(f"  Error: {abs(pred_ratio_vol - cos2_theta_w)/cos2_theta_w*100:.2f}%")

if __name__ == "__main__":
    search_z_boson_brunnian()
