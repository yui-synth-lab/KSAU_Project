
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
    
    quark_info = {}
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
        quark_info[qk] = {
            'z': evaluate_at_x(parse_vector(row['jones_polynomial_vector']), x_val),
            'sig': int(row['signature'])
        }

    target_signs = np.array([[1, 1, 1], [-1, 1, 1], [1, -1, 1]])
    
    def check(v_complex):
        derived_signs = np.sign(np.real(v_complex))
        for r2 in [1, -1]:
            for r3 in [1, -1]:
                for c1 in [1, -1]:
                    for c2 in [1, -1]:
                        for c3 in [1, -1]:
                            transform = np.array([[1*c1, 1*c2, 1*c3], [r2*c1, r2*c2, r2*c3], [r3*c1, r3*c2, r3*c3]])
                            if np.all((derived_signs * transform) == target_signs):
                                return True
        return False

    # Rule 1: Vector Difference with Signature Phase
    # Phase = Angle(Z_u - Z_d) + pi * (sig_u + sig_d) / 2
    v1 = np.zeros((3, 3), dtype=complex)
    for i, u in enumerate(up_types):
        for j, d in enumerate(down_types):
            v1[i, j] = (quark_info[u]['z'] - quark_info[d]['z']) * np.exp(1j * np.pi * (quark_info[u]['sig'] + quark_info[d]['sig']) / 2.0)
    print(f"Rule 1 (sig sum): {check(v1)}")

    # Rule 2: Vector Difference with Signature Difference Phase
    v2 = np.zeros((3, 3), dtype=complex)
    for i, u in enumerate(up_types):
        for j, d in enumerate(down_types):
            v2[i, j] = (quark_info[u]['z'] - quark_info[d]['z']) * np.exp(1j * np.pi * (quark_info[u]['sig'] - quark_info[d]['sig']) / 2.0)
    print(f"Rule 2 (sig diff): {check(v2)}")

    # Rule 3: Ratio with Signature Phase
    v3 = np.zeros((3, 3), dtype=complex)
    for i, u in enumerate(up_types):
        for j, d in enumerate(down_types):
            v3[i, j] = (quark_info[u]['z'] / quark_info[d]['z']) * np.exp(1j * np.pi * (quark_info[u]['sig'] + quark_info[d]['sig']) / 2.0)
    print(f"Rule 3 (ratio sig sum): {check(v3)}")

if __name__ == "__main__":
    main()
