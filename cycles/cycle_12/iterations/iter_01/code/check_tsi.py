
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import json

# Setup SSoT path
sys.path.insert(0, r"E:\Obsidian\KSAU_Project\ssot")
from ksau_ssot import SSOT

def parse_val(val):
    if pd.isnull(val):
        return 0.0
    s = str(val).strip()
    if s == "undefined" or s == "Not Hyperbolic" or s == "N/A" or s == "":
        return 0.0
    if "{" in s or "[" in s:
        import re
        nums = re.findall(r'-?\d+', s)
        if nums:
            return float(nums[0])
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0

def main():
    ssot = SSOT()
    topo_assignments = ssot.topology_assignments()
    knots_df, links_df = ssot.knot_data()
    
    results = []
    
    for particle, info in topo_assignments.items():
        topo_name = info['topology']
        is_link = "L" in topo_name
        df_source = links_df if is_link else knots_df
        
        match = df_source[df_source['name'] == topo_name]
        if match.empty:
            print(f"Warning: {particle} topology {topo_name} not found.")
            continue
            
        inv = match.iloc[0]
        n = parse_val(inv['crossing_number'])
        u = parse_val(inv['unlinking_number']) if is_link else parse_val(inv['unknotting_number'])
        s = parse_val(inv['signature'])
        
        # Formula A: n + u + |s| (Used in Cycle 10 code)
        tsi_a = n + u + abs(s)
        
        # Formula B: n * u / |s| (Described in SSoT constants/Roadmap)
        abs_s = abs(s)
        if abs_s == 0:
            # Handle division by zero. Often in topology s=0 means a specific class.
            # In Cycle 10, they used the sum, so 0 was fine.
            # If the roadmap says n*u/|s|, we need a convention for s=0.
            # Let's see if s is 0 for many particles.
            tsi_b = np.nan
        else:
            tsi_b = (n * u) / abs_s
            
        results.append({
            "name": particle,
            "topology": topo_name,
            "n": n,
            "u": u,
            "s": s,
            "tsi_sum": tsi_a,
            "tsi_prod_div": tsi_b
        })
        
    df = pd.DataFrame(results)
    print(df.to_string())

if __name__ == "__main__":
    main()
