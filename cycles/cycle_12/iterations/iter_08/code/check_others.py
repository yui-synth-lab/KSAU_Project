
import sys
sys.path.insert(0, r"E:\Obsidian\KSAU_Project\ssot")
from ksau_ssot import SSOT
ssot = SSOT()
knots_df, _ = ssot.knot_data()

for name in ['12a_462', '12a_125']:
    k = knots_df[knots_df['name'] == name].iloc[0]
    print(f"Knot: {k['name']}, n={k['crossing_number']}, u={k['unknotting_number']}, s={k['signature']}")
