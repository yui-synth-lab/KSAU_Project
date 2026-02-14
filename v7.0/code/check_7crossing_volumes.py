
import csv

file_path = 'data/knotinfo_data_complete.csv'
knots_to_check = [f"7_{i}" for i in range(1, 8)] + [f"6_{i}" for i in range(1, 4)] + [f"8_{i}" for i in range(1, 5)]

with open(file_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='|')
    results = {}
    for row in reader:
        if row['name'] in knots_to_check:
            results[row['name']] = row['volume']
    
    for k in knots_to_check:
        print(f"Knot: {k:4} | Volume: {results.get(k, 'N/A')}")
