import pandas as pd
import ast

# Load data
df = pd.read_csv(r'E:\Obsidian\KSAU_Project\data\knotinfo_data_complete.csv', sep='|', skiprows=[1], low_memory=False)

# Select relevant columns
cols = ['name', 'volume', 'determinant', 'torsion_numbers']
subset = df[cols].head(20)

print(subset.to_string())
