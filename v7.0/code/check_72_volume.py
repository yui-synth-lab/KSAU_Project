
import csv

file_path = 'data/knotinfo_data_complete.csv'
target_knot = '7_2'

with open(file_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='|')
    for row in reader:
        if row['name'] == target_knot:
            print(f"Knot: {row['name']}")
            print(f"Volume: {row['volume']}")
            print(f"Chern-Simons: {row['chern_simons_invariant']}")
            break
