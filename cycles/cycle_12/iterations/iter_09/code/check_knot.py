
import sys
import pandas as pd
from pathlib import Path

data_dir = Path(r"E:\Obsidian\KSAU_Project\data")
knot_path = data_dir / "knotinfo_data_complete.csv"

df = pd.read_csv(knot_path, sep='|', skiprows=[1], low_memory=False)
match = df[df['name'] == '3_1']
print(match[['name', 'crossing_number', 'unknotting_number', 'signature']].to_string())
