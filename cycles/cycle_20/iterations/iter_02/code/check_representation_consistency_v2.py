import sys
from pathlib import Path
import json
import pandas as pd
import math

# SSOT Setup
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
ssot_path = project_root / "ssot"
sys.path.insert(0, str(ssot_path))    
from ksau_ssot import SSOT

def analyze_consistency():
    ssot = SSOT()
    consts = ssot.constants()
    math_consts = consts.get("mathematical_constants", {})
    assignments = ssot.topology_assignments()
    
    # [Fix Problem 1]: Explicitly verify resonance condition using constants
    kappa = math_consts.get("kappa")
    pi = math_consts.get("pi")
    k_res = math_consts.get("k_resonance")
    
    print("### Resonance Condition Verification ###")
    if kappa and pi and k_res:
        calc_pi = k_res * kappa
        error = abs(calc_pi - pi)
        print(f"k_resonance ({k_res}) * kappa ({kappa:.6f}) = {calc_pi:.6f}")
        print(f"Target pi: {pi:.6f}")
        print(f"Relative Error: {error/pi:.2e}")
    else:
        print("Error: Missing resonance constants in SSoT.")
    print()

    # Define groups for 12 particles
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

    print("\n### Theoretical Context & Observation ###")
    print("24-cell vertices: 24 (Roots of D4)")
    # [Fix Problem 3]: Refined claim regarding W(D4) representations
    # W(D4) order 192, irrep dimensions: 1, 1, 2, 3, 3, 3, 3, 4, 4, 6, 6, 8
    print("Symmetry group W(D4) irrep dimensions: 1, 1, 2, 3, 3, 3, 3, 4, 4, 6, 6, 8")
    print("Observation: The Standard Model gauge group dimensions (8, 3, 1) are a subset of W(D4) irreps.")
    print("Note: This is an observation of inclusion rather than a unique derivation.")

if __name__ == "__main__":
    analyze_consistency()
