
import sys
import pandas as pd
import numpy as np
import json
from pathlib import Path
import re

# Standard AIRDP Researcher header
sys.path.insert(0, r"E:\Obsidian\KSAU_Project\ssot")
from ksau_ssot import SSOT

def parse_val(val):
    if pd.isnull(val):
        return 0.0
    s = str(val).strip()
    if s == "undefined" or s == "Not Hyperbolic" or s == "N/A" or s == "":
        return 0.0
    # Handle list-like strings [1, 2] or {1, 2}
    if "[" in s or "{" in s:
        nums = re.findall(r'-?\d+', s)
        return float(nums[0]) if nums else 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0

def main():
    ssot = SSOT()
    topo_assignments = ssot.topology_assignments()
    knots_df, links_df = ssot.knot_data()
    params = ssot.parameters()
    
    # 1. Collect all particles with measured lifetimes
    particle_data = []
    
    for sector in ['quarks', 'leptons', 'bosons']:
        for name, info in params[sector].items():
            tau = info.get('lifetime_s')
            if tau is None:
                continue
            
            # Get topology
            topo_info = topo_assignments.get(name)
            if not topo_info:
                continue
            
            topo_name = topo_info['topology']
            is_link = "L" in topo_name
            df_source = links_df if is_link else knots_df
            
            match = df_source[df_source['name'] == topo_name]
            if match.empty:
                print(f"Warning: {name} topology {topo_name} not found.")
                continue
                
            inv = match.iloc[0]
            n = parse_val(inv['crossing_number'])
            # KnotInfo uses 'unknotting_number', LinkInfo uses 'unlinking_number'
            u = parse_val(inv.get('unlinking_number')) if is_link else parse_val(inv.get('unknotting_number'))
            s = parse_val(inv['signature'])
            
            particle_data.append({
                "name": name,
                "tau": tau,
                "n": n,
                "u": u,
                "s": s
            })
            
    df = pd.DataFrame(particle_data)
    print("Extracted Data for Decaying Particles:")
    print(df.to_string())

if __name__ == "__main__":
    main()
