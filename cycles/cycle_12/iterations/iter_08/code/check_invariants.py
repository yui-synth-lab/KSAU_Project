
import sys
sys.path.insert(0, r"E:\Obsidian\KSAU_Project\ssot")
from ksau_ssot import SSOT
ssot = SSOT()
knots_df, _ = ssot.knot_data()

k = knots_df[knots_df['name'] == '12a_435'].iloc[0]
print(f"Knot: {k['name']}")
print(f"Crossing (n): {k['crossing_number']}")
print(f"Unknotting (u): {k['unknotting_number']}")
print(f"Signature (s): {k['signature']}")
