import pandas as pd
import numpy as np

# Path to the ultimate raw data
raw_data_path = "KSAU/publish/data/linkinfo_data_complete.csv"
output_candidates = "KSAU/publish/v2.3/data/link_candidates_3comp.csv"

print("Reading linkinfo_data_complete.csv...")
# The file uses '|' as delimiter
# Based on read_file output, row 0 is names, row 1 is descriptions.
# We skip row 1.
df = pd.read_csv(raw_data_path, sep='|', skiprows=[1], low_memory=False)

print(f"Total entries: {len(df)}")

# 1. Filter for 3-component links
# The 'components' column contains the number of components
df['components'] = pd.to_numeric(df['components'], errors='coerce')
df_3c = df[df['components'] == 3].copy()

print(f"3-component links found: {len(df_3c)}")

# 2. Filter for hyperbolic links (volume > 0)
df_3c['volume'] = pd.to_numeric(df['volume'], errors='coerce')
df_3c = df_3c[df_3c['volume'] > 0].copy()

# 3. Extract relevant columns for KSAU
# name, crossing_number, volume, signature, linking_matrix
# Note: 'signature' and 'volume' might have NaN if not calculated
cols = ['name', 'crossing_number', 'volume', 'signature', 'linking_matrix', 'components']
df_final = df_3c[cols].copy()

# Drop rows where critical invariants are missing
df_final = df_final.dropna(subset=['volume', 'signature'])

print(f"Final valid candidates: {len(df_final)}")

# 4. Sort by volume (The primary KSAU mass indicator)
df_final = df_final.sort_values('volume')

# Save to v2.3 data directory
df_final.to_csv(output_candidates, index=False)
print(f"Saved candidate list to {output_candidates}")

print("")
print("[Low Volume 3-Component Links (Mass Ground States)]")
print(df_final.head(10))