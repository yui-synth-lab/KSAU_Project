
import sys
import pandas as pd
from pathlib import Path

data_dir = Path(r"E:\Obsidian\KSAU_Project\data")
link_path = data_dir / "linkinfo_data_complete.csv"

df = pd.read_csv(link_path, sep='|', skiprows=[1], low_memory=False)
match = df[df['name'] == 'L11a225{1}']
print(match[['name', 'crossing_number', 'unlinking_number', 'signature']].to_string())
