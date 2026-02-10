import pandas as pd
import re
import numpy as np
import sys
import os

# Add v6.1 code path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../v6.1/code'))
import utils_v61

def check_brunnian_hierarchy():
    # 1. Load Data
    consts = utils_v61.load_constants()
    topo = utils_v61.load_assignments()
    links = pd.read_csv('data/linkinfo_data_complete.csv', sep='|', skiprows=[1])
    links['v'] = pd.to_numeric(links['volume'], errors='coerce')
    links['c'] = pd.to_numeric(links['components'], errors='coerce')

    def is_brunnian(matrix):
        nums = re.findall(r'-?\d+', str(matrix))
        return all(n == '0' for n in nums) if nums else False

    links['is_br'] = links['linking_matrix'].apply(is_brunnian)
    
    br3 = links[links['is_br'] & (links['c'] == 3)].copy()
    br3 = br3[br3['v'] > 0].sort_values('v').drop_duplicates('v')
    
    print("--- 3-Component Brunnian Link Volume Hierarchy ---")
    print(f"{'Name':<12} | {'Volume':<10} | {'Ratio to Borromean'}")
    print("-" * 45)
    
    # Borromean Rings volume
    v_borr = consts['v_borromean']
    
    for _, row in br3.iterrows():
        ratio = row['v'] / v_borr
        print(f"{row['name']:<12} | {row['v']:<10.6f} | {ratio:.6f}")

    print("\n--- Geometric Analysis ---")
    
    v_w = topo['W']['volume']
    v_z = topo['Z']['volume']
    
    print(f"W ({topo['W']['topology']}) / Borr: {v_w / v_borr:.4f}")
    print(f"Z ({topo['Z']['topology']}) / Borr: {v_z / v_borr:.4f}")
    
    v_tet = 1.01494
    
    # Check if Z = W + something special
    diff_zw = v_z - v_w
    print(f"Z - W: {diff_zw:.6f}")
    
    # Look for 2-component Brunnian for Higgs
    br2 = links[links['is_br'] & (links['c'] == 2)].copy()
    br2 = br2[br2['v'] > 0].sort_values('v').drop_duplicates('v')
    print("\n--- 2-Component Brunnian Hierarchy (Higgs) ---")
    for _, row in br2.iterrows():
         if 10 < row['v'] < 20:
             print(f"{row['name']:<12} | {row['v']:<10.6f} | Ratio to Borr: {row['v']/v_borr:.4f}")

if __name__ == "__main__":
    check_brunnian_hierarchy()