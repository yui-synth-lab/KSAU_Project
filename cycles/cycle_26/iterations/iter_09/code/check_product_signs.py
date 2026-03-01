
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import json
import re

# Setup SSOT
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
ssot_path = project_root / "ssot"
sys.path.insert(0, str(ssot_path))    
from ksau_ssot import SSOT

def parse_vector(vec_str):
    if not isinstance(vec_str, str) or pd.isna(vec_str): return None
    clean_str = vec_str.strip('[]{}')
    parts = re.split(r',\s*', clean_str)
    try:
        nums = [int(p) for p in parts]
        return nums[0], nums[1], nums[2:]
    except: return None

def evaluate_at_x(vector, x_val):
    if vector is None: return 0j
    min_pow, max_pow, coeffs = vector
    val = 0j
    for i, c in enumerate(coeffs):
        p = min_pow + i
        val += c * (x_val ** p)
    return val

def main():
    ssot = SSOT()
    knots_df, links_df = ssot.knot_data()
    topo_assignments = ssot.topology_assignments()
    
    quarks = ["Up", "Charm", "Top", "Down", "Strange", "Bottom"]
    up_types = ["Up", "Charm", "Top"]
    down_types = ["Down", "Strange", "Bottom"]
    
    quark_z = {}
    x_val = np.exp(1j * np.pi / 24)
    
    for qk in quarks:
        topo_name = topo_assignments[qk]['topology']
        row = links_df[links_df['name'] == topo_name]
        if row.empty: row = knots_df[knots_df['name'] == topo_name]
        if row.empty:
            base_name = topo_name.split('{')[0]
            row = links_df[links_df['name'] == base_name]
            if row.empty: row = knots_df[knots_df['name'] == base_name]
            if row.empty: row = links_df[links_df['name'].str.startswith(base_name + "{")]
        row = row.iloc[0]
        quark_z[qk] = evaluate_at_x(parse_vector(row['jones_polynomial_vector']), x_val)

    target_signs = np.array([[1, 1, 1], [-1, 1, 1], [1, -1, 1]])
    
    print("Rule: Phase = Angle(Z_u * conj(Z_d))")
    v_complex = np.zeros((3, 3), dtype=complex)
    for i, u in enumerate(up_types):
        for j, d in enumerate(down_types):
            v_complex[i, j] = quark_z[u] * np.conj(quark_z[d])
    
    derived_signs = np.sign(np.real(v_complex))
    
    best_match = 0
    best_transformed = None
    for r2 in [1, -1]:
        for r3 in [1, -1]:
            for c1 in [1, -1]:
                for c2 in [1, -1]:
                    for c3 in [1, -1]:
                        transform = np.array([[1*c1, 1*c2, 1*c3], [r2*c1, r2*c2, r2*c3], [r3*c1, r3*c2, r3*c3]])
                        trial = derived_signs * transform
                        match = np.sum(trial == target_signs)
                        if match > best_match:
                            best_match = match
                            best_transformed = trial
    
    print(f"Best match: {best_match}/9")
    if best_match == 9:
        print("FOUND 100% MATCH with Product Rule and Gauge Flips!")
    else:
        print("Mismatches:")
        for i in range(3):
            for j in range(3):
                if best_transformed[i, j] != target_signs[i, j]:
                    print(f"  {up_types[i]}-{down_types[j]}: Derived {best_transformed[i, j]}, Target {target_signs[i, j]}")

if __name__ == "__main__":
    main()
