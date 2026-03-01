import sys
import numpy as np
from pathlib import Path
import pandas as pd
import re

# Resolve project root relative to this file
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / 'ssot'))
from ksau_ssot import SSOT

def parse_vector(vec_str):
    if not isinstance(vec_str, str) or pd.isna(vec_str): return None
    clean_str = vec_str.strip('[]{}')
    parts = re.split(r',\s*', clean_str)
    try:
        nums = [int(p) for p in parts]
        return nums[0], nums[1], nums[2:]
    except: return None

def evaluate(vector, q, is_link):
    if vector is None: return 0j
    min_pow, max_pow, coeffs = vector
    val = 0j
    for i, c in enumerate(coeffs):
        p = min_pow + i
        if is_link: val += c * (q ** (p / 2.0))
        else: val += c * (q ** p)
    return val

def main():
    ssot = SSOT()
    knots_df, links_df = ssot.knot_data()
    topo_assignments = ssot.topology_assignments()
    q_val = np.exp(2j * np.pi / 24)
    
    quark_z = {}
    for qk in ['Up', 'Charm', 'Down', 'Strange']:
        topo = topo_assignments[qk]['topology']
        row = knots_df[knots_df['name'] == topo]
        is_link = False
        if row.empty:
            row = links_df[links_df['name'] == topo]
            is_link = True
        
        vec_str = row.iloc[0]['jones_polynomial_vector']
        quark_z[qk] = evaluate(parse_vector(vec_str), q_val, is_link)
        
    u1, u2 = quark_z['Up'], quark_z['Charm']
    d1, d2 = quark_z['Down'], quark_z['Strange']
    
    z = ((u1 - d1) * (u2 - d2)) / ((u1 - d2) * (u2 - d1))
    print(f"z: {z}")
    
if __name__ == "__main__":
    main()
