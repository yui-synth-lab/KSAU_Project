import pandas as pd
import sys
from pathlib import Path

# SSoT Loader Setup
sys.path.insert(0, r"E:\Obsidian\KSAU_Project\ssot")
from ksau_ssot import SSOT

def main():
    ssot = SSOT()
    knots_df, links_df = ssot.knot_data()
    
    targets = ["L8a18{0,1}", "L11n330{0,1}", "L11a528{0,1}"]
    for name in targets:
        match = links_df[links_df['name'] == name]
        if not match.empty:
            print(f"Name: {name}")
            print(f"Signature: {match.iloc[0]['signature']}")
            print("-" * 20)
        else:
            print(f"Name: {name} not found")

if __name__ == "__main__":
    main()
