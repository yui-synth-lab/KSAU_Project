import pandas as pd
import warnings

warnings.filterwarnings('ignore')

# Load data
links = pd.read_csv('data/linkinfo_data_complete.csv', sep='|')
links['components'] = pd.to_numeric(links['components'], errors='coerce')
links = links[links['components'] == 3]
links['volume'] = pd.to_numeric(links['volume'], errors='coerce')
links = links.dropna(subset=['volume'])
links = links[links['volume'] > 0]

# Sort by volume
links = links.sort_values('volume')

print("Top 20 3-component links by Volume:")
print(links[['name', 'crossing_number', 'volume', 'signature', 'determinant']].head(20))

# Check for our bosons
bosons = ['L11n387', 'L11a431']
for b in bosons:
    match = links[links['name'].str.contains(b, na=False)]
    if not match.empty:
        vol = match.iloc[0]['volume']
        pos = (links['volume'] < vol).sum()
        total = len(links)
        print(f"\nBoson {b} position in 3-comp volume spectrum:")
        print(f"Rank: {pos}/{total} (Top {pos/total*100:.2f}%)")
        print(match[['name', 'crossing_number', 'volume']])