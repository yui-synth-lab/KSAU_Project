import pandas as pd

# Path to the link info CSV
path = r"E:\Obsidian\KSAU_Project\data\linkinfo_data_complete.csv"

# Load the CSV
df = pd.read_csv(path, sep="|")

# Find L11a225{1}
top_topo = "L11a225{1}"
row = df[df['name'] == top_topo]

if not row.empty:
    cols = ['name', 'crossing_number', 'components', 'determinant', 'signature', 'unlinking_number', 'splitting_number', 'arf_invariant']
    print(row[cols].to_string(index=False))
else:
    print(f"Topology {top_topo} not found.")
