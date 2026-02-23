import sys
import pandas as pd
import json
from pathlib import Path

sys.path.insert(0, r"E:\Obsidian\KSAU_Project\ssot")
from ksau_ssot import SSOT

def main():
    ssot = SSOT()
    knots_df, links_df = ssot.knot_data()
    topo = ssot.topology_assignments()
    
    results = {}
    
    for name, info in topo.items():
        t_name = info['topology']
        if 'L' in t_name:
            match = links_df[links_df['name'] == t_name]
            if match.empty:
                # Try unoriented or name_rank?
                match = links_df[links_df['name'].str.contains(t_name.replace('{','\{').replace('}','\}'), na=False)]
        else:
            match = knots_df[knots_df['name'] == t_name]
            
        if not match.empty:
            torsion = match.iloc[0].get('torsion_numbers', "N/A")
            results[name] = {
                "topology": t_name,
                "torsion_numbers": torsion
            }
        else:
            results[name] = {
                "topology": t_name,
                "torsion_numbers": "NOT_FOUND"
            }
            
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
