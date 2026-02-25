
import pandas as pd
from pathlib import Path

data_dir = Path(r"E:\Obsidian\KSAU_Project\data")
knot_path = data_dir / "knotinfo_data_complete.csv"

# Read only necessary columns
# name is column 0, torsion_numbers is column 146 (0-indexed)
# Wait, column index 147 in head -n 2 output was "torsion_numbers"
# Let's find the index by reading header.

with open(knot_path, 'r', encoding='utf-8') as f:
    header = f.readline().strip().split('|')

name_idx = header.index('name')
torsion_idx = header.index('torsion_numbers')

print(f"Name index: {name_idx}, Torsion index: {torsion_idx}")

df = pd.read_csv(knot_path, sep='|', skiprows=[1], low_memory=False)
target_knots = ["3_1", "4_1", "6_1"]
subset = df[df['name'].isin(target_knots)]

for _, row in subset.iterrows():
    print(f"Knot: {row['name']}, Torsion: {row['torsion_numbers']}")
