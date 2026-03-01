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
    
    # 2. Calculate Target Volume V_Z using Boson Scaling Law
    kappa = consts['kappa']
    G = consts['G_catalan']
    A_fermi = 10 * kappa
    A_boson = (3/7) * G  # v6.3 Boson Slope
    
    # Intercepts
    C_fermi = -(7 + 7 * kappa)
    # C_boson is derived from W-boson baseline in physical_constants.json if available
    # Or calculated here for consistency
    mw_obs = consts['bosons']['W']['observed_mass']
    topo_assignments = utils_v61.load_assignments()
    vw_phys = topo_assignments['W']['volume']
    C_boson = np.log(mw_obs) - A_boson * vw_phys
    
    # Z Boson Mass (Experimental)
    mz_mev = consts['bosons']['Z']['observed_mass']
    target_vol = (np.log(mz_mev) - C_boson) / A_boson
    print(f"Target Volume for M_Z ({mz_mev} MeV): {target_vol:.4f} (using Boson Law)")
    
    # 3. Filter for candidates
    # ... (filter logic remains same)
    
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
        
        # Brunnian check
        lm = str(row.get('linking_matrix', ''))
        nums = re.findall(r'-?\d+', lm)
        is_brunnian = all(n == '0' for n in nums) if nums else False
        
        if is_brunnian or diff < 0.1:
            br_str = "YES" if is_brunnian else "No"
            print(f"{row['name']:<12} | {vol:.4f}   | {br_str:<9} | {diff:.4f}")

    # 4. Hypothesis: The Z-W mass ratio is governed by the Master Constant kappa
    print("\n[Electroweak Unified Verification: The Neutral Twist Hypothesis]")
    # V_W is the Double Borromean baseline
    vw = vw_phys
    kappa = consts['kappa']
    
    # NEW THEORY: Z is W with one unit of topological twist (kappa)
    vz_theo = vw + kappa
    vz_actual = topo_assignments['Z']['volume']
    print(f"  Theoretical V_Z (V_W + kappa): {vz_theo:.4f}")
    print(f"  Current Assigned V_Z         : {vz_actual:.4f}")
    
    # Weinberg Angle prediction: cos^2(theta_w) = exp(-2 * kappa)
    # This implies the electroweak mixing slope is exactly 1.0
    pred_cos2_kappa = np.exp(-2 * kappa)
    
    sin2w_exp = consts['sin2theta_w']
    cos2w_exp = 1.0 - sin2w_exp
    
    print(f"\n[Rho Parameter & Weinberg Angle]")
    print(f"  Experimental cos^2(theta_W) : {cos2w_exp:.4f}")
    print(f"  KSAU Predicted exp(-2*kappa): {pred_cos2_kappa:.4f}")
    
    error = abs(pred_cos2_kappa - cos2w_exp) / cos2w_exp * 100
    print(f"  Residual Error              : {error:.4f}%")
    
    if error < 0.2:
        print("\n  SUCCESS: The Electroweak gap is exactly one Master Constant (pi/24)!")
        print("  The Z boson mass is the 'Twisted' state of the W vacuum.")

if __name__ == "__main__":
    search_z_boson_brunnian()
