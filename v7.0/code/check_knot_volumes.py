
import csv

file_path = 'data/knotinfo_data_complete.csv'
knots = ['4_1', '5_2', '6_1', '6_2', '6_3', '7_2', '8_1']

with open(file_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='|')
    results = {}
    for row in reader:
        if row['name'] in knots:
            results[row['name']] = row['volume']
    
    for k in knots:
        print(f"Knot: {k:4} | Volume: {results.get(k, 'N/A')}")
