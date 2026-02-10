import pandas as pd
import json
import warnings

warnings.filterwarnings('ignore')

# Load data
knots = pd.read_csv('data/knotinfo_data_complete.csv', sep='|')
links = pd.read_csv('data/linkinfo_data_complete.csv', sep='|')

# Target assignments (base names)
assignments = {
    'Electron': {'pattern': '3_1', 'type': 'knot'},
    'Muon': {'pattern': 'L9a21', 'type': 'link'},
    'Tau': {'pattern': 'L11a88', 'type': 'link'},
    'W-boson': {'pattern': 'L11n387', 'type': 'link'},
    'Z-boson': {'pattern': 'L11a431', 'type': 'link'},
    'Top-quark': {'pattern': 'L10n95', 'type': 'link'}
}

results = {}

for p, info in assignments.items():
    pattern = info['pattern']
    if info['type'] == 'knot':
        row = knots[knots['name'].str.contains(f"^{pattern}$", na=False)]
    else:
        # Link names often have suffixes like {0}, {1}
        row = links[links['name'].str.contains(f"^{pattern}", na=False)]
    
    if not row.empty:
        r = row.iloc[0]
        results[p] = {
            'topology': r['name'],
            'crossing_number': r.get('crossing_number'),
            'volume': r.get('volume'),
            'signature': r.get('signature'),
            'determinant': r.get('determinant'),
        }
        if info['type'] == 'link':
            results[p]['components'] = r.get('components')
    else:
        results[p] = "NOT FOUND"

print(json.dumps(results, indent=2))