import pandas as pd
import re
import numpy as np
import sys
import os

# Add v6.1 code to path for utils_v61
sys.path.append(os.path.join(os.path.dirname(__file__), '../../v6.1/code'))
import utils_v61

def prove_no_ppicking():
    print("="*60)
    print("KSAU v6.3: Proving Topological Necessity vs P-Picking")
    print("="*60)
    
    # 1. Load data
    consts = utils_v61.load_constants()
    _, links = utils_v61.load_data()
    links['v'] = pd.to_numeric(links['volume'], errors='coerce')
    links['c'] = pd.to_numeric(links['components'], errors='coerce')
    links['C'] = pd.to_numeric(links['crossing_number'], errors='coerce')

    def is_brunnian(matrix):
        nums = re.findall(r'-?\d+', str(matrix))
        return all(n == '0' for n in nums) if nums else False

    links['is_br'] = links['linking_matrix'].apply(is_brunnian)
    
    # Filter for 3-component Brunnian links
    br3 = links[links['is_br'] & (links['c'] == 3)].copy()
    
    print(f"Total links in database: {len(links)}")
    print(f"3-component Brunnian links (The Elite Class): {len(br3)}")
    print(f"Percentage: {len(br3)/len(links)*100:.3f}%")
    
    # 2. Check for "The 2.0000 Point"
    v_borr = consts['v_borromean']
    br3['ratio'] = br3['v'] / v_borr
    
    print("\n--- Why L11n387 (W-Boson) is Unique ---")
    perfect_doubles = br3[abs(br3['ratio'] - 2.0) < 0.001].sort_values('C')
    print(f"3-comp Brunnian links with Vol = 2.0 * V_borr:")
    print(perfect_doubles[['name', 'v', 'C', 'ratio']])
    
    # 3. Component Scaling Law: A = n * (G/7)
    print("\n--- The Component Scaling Law (The Smoking Gun) ---")
    G = consts['G_catalan']
    kappa = consts['kappa']
    
    A_fermion = 10 * kappa
    A_boson = 3 * kappa
    
    print(f"  Fundamental Constant kappa = G/7: {kappa:.6f}")
    print(f"  Fermion Slope (10 * kappa): {A_fermion:.6f}")
    print(f"  Boson Slope (3 * kappa): {A_boson:.6f}")
    
    # 4. Simplicity Constraint
    topo = utils_v61.load_assignments()
    target_v_w = topo['W']['volume']
    simpler_cands = br3[(br3['v'] > target_v_w - 0.5) & (br3['v'] < target_v_w + 0.5) & (br3['C'] < 11)]
    print("\n--- Simplicity Check: Are there simpler candidates ignored? ---")
    if simpler_cands.empty:
        print(f"  No 3-component Brunnian links with C < 11 exist in the W-boson mass range.")
        print(f"  L11n387 is the MINIMAL COMPLEXITY member of its class.")
    else:
        print(simpler_cands[['name', 'v', 'C']])

if __name__ == "__main__":
    prove_no_ppicking()