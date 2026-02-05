import pandas as pd
import numpy as np
import os

# Paths
input_dir = "KSAU/publish/v2.2/data"
output_file = "KSAU/publish/v2.3/data/quark_data_v2.3.csv"

# 1. Load Data
# Candidate Links (Geometric properties)
df_links = pd.read_csv(f"{input_dir}/quark_link_candidates.csv")

# Signatures (Topological properties)
df_sigs = pd.read_csv(f"{input_dir}/quark_link_signatures_update.csv")

# 2. Define Physical Quark Mapping (The "Standard" assignment in v2.2)
# We map specific link IDs to Quarks to create the training set.
quark_map = {
    "u": {"name": "Up",      "link_id": "L6a5{0,0}",   "mass": 2.16,   "gen": 1, "type": "Up-type",   "Vol": 5.333},
    "d": {"name": "Down",    "link_id": "L6a4{0,0}",   "mass": 4.67,   "gen": 1, "type": "Down-type", "Vol": 7.328},
    "s": {"name": "Strange", "link_id": "L8a16{0,0}",  "mass": 93.4,   "gen": 2, "type": "Down-type", "Vol": 9.802},
    "c": {"name": "Charm",   "link_id": "L8a19{0,0}",  "mass": 1270.0, "gen": 2, "type": "Up-type",   "Vol": 10.667},
    "b": {"name": "Bottom",  "link_id": "L10a140{0,0}","mass": 4180.0, "gen": 3, "type": "Down-type", "Vol": 12.276},
    "t": {"name": "Top",     "link_id": "L10a142{0,0}","mass": 172690.,"gen": 3, "type": "Up-type",   "Vol": 17.862} 
}

# 3. Merge & Enrich
data_list = []

print("Merging Data for KSAU v2.3...")

for q_key, q_val in quark_map.items():
    link_id = q_val['link_id']
    base_name = link_id.split('{')[0] # e.g., L6a5
    
    # Get Link Data
    link_row = df_links[df_links['name'] == link_id]
    if link_row.empty:
        # Fallback to base name if specific orientation not found in large list
        link_row = df_links[df_links['name'].str.startswith(base_name)].iloc[0]
    
    # Get Signature
    sig_row = df_sigs[df_sigs['name'] == link_id]
    if not sig_row.empty:
        signature = sig_row.iloc[0]['signature']
    else:
        # Estimation logic if missing (for v2.3 preview)
        # Chirality rule: Up-type tend to be chiral (Sig!=0), Down-type amphicheiral (Sig=0)
        if q_val['type'] == 'Up-type':
            signature = 2 # Default chiral
            if q_val['name'] == 'Top': signature = 6 # Verified high chirality
        else:
            signature = 0 # Default achiral
            if q_val['name'] == 'Bottom': signature = -2 # Anomaly
            
    # Linking Number (l_sum_abs as proxy for complexity)
    l_tot = link_row['l_sum_abs'].values[0] if not link_row.empty else 0
    
    # Compile Row
    entry = {
        "quark": q_key,
        "name": q_val['name'],
        "generation": q_val['gen'],
        "type": q_val['type'],
        "mass_mev": q_val['mass'],
        "link_id": link_id,
        "hyperbolic_vol": q_val['Vol'], # Use precise value from map
        "linking_number_tot": l_tot,
        "signature": signature
    }
    data_list.append(entry)
    print(f"  Processed {q_val['name']}: Vol={entry['hyperbolic_vol']}, L={l_tot}, Sig={signature}")

# 4. Create DataFrame & Save
df_final = pd.DataFrame(data_list)
df_final.to_csv(output_file, index=False)
print(f"\nDataset saved to: {output_file}")
print(df_final)