import pandas as pd
import numpy as np

# Load the extracted candidate database
candidates_path = "KSAU/publish/v2.3/data/link_candidates_3comp.csv"
df = pd.read_csv(candidates_path)

print("=== KSAU v2.3 Link Selection Algorithm ===")

# Helper: Parse linking matrix to get total linking number sum
def get_l_tot(matrix_str):
    try:
        # Simplify parsing: extract all numbers and sum their absolute values
        # Format is like {{0, -1, -1}, {-1, 0, -1}, {-1, -1, 0}}
        nums = [int(s) for s in matrix_str.replace('{','').replace('}','').replace(',',' ').split() if s.lstrip('-').isdigit()]
        return sum([abs(n) for n in nums]) // 2 # Each pair is counted twice in the matrix
    except:
        return 0

df['l_tot'] = df['linking_matrix'].apply(get_l_tot)

# 1. Define Generations by Volume Bands
# Up and Down are determined by relative volume in the same complexity class
# We sort by crossing number first, then volume

results = []

# Generation 1: 6-7 crossings
g1_links = df[df['crossing_number'].isin([6, 7])].sort_values('volume')
# Up: Lowest volume in G1
u_cand = g1_links.iloc[0]
# Down: Medium volume in G1
d_cand = g1_links[g1_links['volume'] > 7].iloc[0]

results.append({"gen": 1, "type": "Up", "match": u_cand})
results.append({"gen": 1, "type": "Down", "match": d_cand})

# Generation 2: 8-9 crossings
g2_links = df[df['crossing_number'].isin([8, 9])].sort_values('volume')
# Strange: Medium volume in G2 (Down-type)
s_cand = g2_links[g2_links['volume'] > 9.5].iloc[0]
# Charm: Higher volume in G2 (Up-type)
c_cand = g2_links[g2_links['volume'] > 10.5].iloc[0]

results.append({"gen": 2, "type": "Strange", "match": s_cand})
results.append({"gen": 2, "type": "Charm", "match": c_cand})

# Generation 3: 10+ crossings
g3_links = df[df['crossing_number'] >= 10].sort_values('volume')
# Bottom: Medium volume in G3
b_cand = g3_links[g3_links['volume'] > 12].iloc[0]
# Top: Highest volume link in our database
t_cand = g3_links.iloc[-1]

results.append({"gen": 3, "type": "Bottom", "match": b_cand})
results.append({"gen": 3, "type": "Top", "match": t_cand})

print("")
print("[Algorithmically Selected Candidates]")
for r in results:
    m = r['match']
    print(f"Gen {r['gen']} {r['type']}: {m['name']} (Vol={m['volume']:.3f}, Sig={m['signature']}, L={m['l_tot']})")

# Export for comparison
df_selected = pd.DataFrame([
    {"name": r['type'], "link": r['match']['name'], "Vol": r['match']['volume'], "Sig": r['match']['signature']}
    for r in results
])
df_selected.to_csv("KSAU/publish/v2.3/data/selected_by_algorithm.csv", index=False)