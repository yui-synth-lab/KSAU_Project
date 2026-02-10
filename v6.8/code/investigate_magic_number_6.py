import pandas as pd
import warnings

warnings.filterwarnings('ignore')

# Load data
links = pd.read_csv('data/linkinfo_data_complete.csv', sep='|')

# Target: Borromean Rings (L6a5) and the Fundamental Unit (L6a4)
targets = ['L6a4', 'L6a5']

print("--- Geometric Properties of Candidate Units ---")
for t in targets:
    # Use pattern matching to find the link (e.g., L6a4{0,0})
    match = links[links['name'].str.contains(f"^{t}", na=False)]
    if not match.empty:
        r = match.iloc[0]
        print(f"\nLink: {t}")
        print(f"  Full Name: {r['name']}")
        print(f"  Volume: {r['volume']}")
        print(f"  Crossing Number: {r['crossing_number']}")
        print(f"  Components: {r['components']}")
        print(f"  Signature: {r['signature']}")
        print(f"  Determinant: {r['determinant']}")
        print(f"  Conway Polynomial: {r['conway_polynomial']}")
        print(f"  Jones Polynomial: {r['jones_polynomial']}")

print("\n--- Searching for the Number 6 ---")
print("Hypothesis: Is there a symmetry group of order 6? Or 6 sub-components?")