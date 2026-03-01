
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
    consts = ssot.constants()
    knots_df, links_df = ssot.knot_data()
    topo_assignments = ssot.topology_assignments()
    
    quarks = ["Up", "Charm", "Top", "Down", "Strange", "Bottom"]
    up_types = ["Up", "Charm", "Top"]
    down_types = ["Down", "Strange", "Bottom"]
    
    quark_z = {}
    x_val = np.exp(1j * np.pi / 12) # Try pi/12
    
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
        z = evaluate_at_x(parse_vector(row['jones_polynomial_vector']), x_val)
        quark_z[qk] = z
        print(f"{qk:7}: {z.real:7.4f} + {z.imag:7.4f}i")

    # Calculate V_ij phases using Z_u / Z_d
    print("Rule: Phase = Angle(Z_u / Z_d)")
    for i, u in enumerate(up_types):
        for j, d in enumerate(down_types):
            v_val = quark_z[u] / quark_z[d]
            phase = np.angle(v_val)
            print(f"V_{u}{d:7}: {phase:7.4f} rad, Sign(Re): {np.sign(v_val.real):2.0f}")

if __name__ == "__main__":
    main()
