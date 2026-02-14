
import csv

file_path = 'data/knotinfo_data_complete.csv'
target_knot = '7_2'

with open(file_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='|')
    for row in reader:
        if row['name'] == target_knot:
            for k, v in row.items():
                if v and not k.endswith('_anon'):
                    print(f"{k}: {v}")
            break
