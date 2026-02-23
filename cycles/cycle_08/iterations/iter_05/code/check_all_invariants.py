import numpy as np
import sys
import json
import pandas as pd
from pathlib import Path

# SSoT Loader setup
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
ssot_dir = project_root / "ssot"
sys.path.insert(0, str(ssot_dir))
from ksau_ssot import SSOT

def parse_val(val, default=0.0):
    if pd.isnull(val): return default
    s = str(val).strip()
    if s == "" or s == "undefined" or s == "Not Hyperbolic": return default
    import re
    nums = re.findall(r'-?\d+', s)
    if nums: return float(nums[0])
    return default

def main():
    ssot = SSOT()
    topo = ssot.topology_assignments()
    knots_df, links_df = ssot.knot_data()
    params = ssot.parameters()
    
    print(f"{'Particle':<10} | {'V':<7} | {'C':<2} | {'N':<3} | {'Det':<5} | {'Sig':<4} | {'Braid':<4}")
    print("-" * 60)
    
    for p_name, info in topo.items():
        topo_name = info['topology']
        if "L" in topo_name:
            match = links_df[links_df['name'] == topo_name]
        else:
            match = knots_df[knots_df['name'] == topo_name]
        
        if not match.empty:
            row = match.iloc[0]
            v = info['volume']
            c = info['components']
            n = parse_val(row['crossing_number'])
            det = parse_val(row['determinant'])
            sig = parse_val(row['signature'])
            braid = parse_val(row['braid_index'])
            print(f"{p_name:<10} | {v:<7.4f} | {c:<2} | {n:<3.0f} | {det:<5.0f} | {sig:<4.0f} | {braid:<4.0f}")

if __name__ == "__main__":
    main()
