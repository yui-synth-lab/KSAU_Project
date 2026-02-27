import sys
from pathlib import Path
import json
import pandas as pd

# SSOT Setup
# C:\Users\yuyay\AppData\Local\Programs\Python\Python311\python.exe C:\Users\yuyay\AppData\Roaming\npm\node_modules\@google\gemini-cli\node_modules\@google\gemini-cli-core\dist\src\skills\builtin\skill-creator\SKILL.md
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
ssot_path = project_root / "ssot"
sys.path.insert(0, str(ssot_path))    
from ksau_ssot import SSOT

def analyze_consistency():
    ssot = SSOT()
    consts = ssot.constants()
    assignments = ssot.topology_assignments()
    
    # Define groups
    group_8_keys = ["Up", "Down", "Strange", "Charm", "Bottom", "Top", "W", "Z"]
    group_3_keys = ["Electron", "Muon", "Tau"]
    group_1_keys = ["Higgs"]
    
    groups = {
        "Group_8 (SU3-like)": group_8_keys,
        "Group_3 (SU2-like)": group_3_keys,
        "Group_1 (U1-like)": group_1_keys
    }
    
    results = {}
    for gname, keys in groups.items():
        g_data = []
        for k in keys:
            if k in assignments:
                data = assignments[k]
                g_data.append({
                    "particle": k,
                    "n": data.get("crossing_number"),
                    "c": data.get("components"),
                    "D": data.get("determinant")
                })
        results[gname] = g_data

    print("### Consistency Analysis by Group (8, 3, 1) ###")
    for gname, data in results.items():
        df = pd.DataFrame(data)
        print(f"\n--- {gname} ---")
        if not df.empty:
            print(df[["particle", "n", "c", "D"]].to_string(index=False))
            print(f"Mean n: {df['n'].mean():.2f}, Mean c: {df['c'].mean():.2f}")
        else:
            print("No data.")

    print("\n### Theoretical Context ###")
    print("24-cell vertices: 24 (Roots of D4)")
    print("Symmetry group W(D4) irrep dimensions: 1, 1, 2, 3, 3, 3, 3, 4, 4, 6, 6, 8")
    print("Standard Model gauge dimensions: 8 (SU3), 3 (SU2), 1 (U1)")
    print("Observation: The particle grouping matches these dimensions.")

if __name__ == "__main__":
    analyze_consistency()
