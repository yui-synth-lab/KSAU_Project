
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
        if len(nums) < 2: return None
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
    
    target_signs = np.array([
        [1, 1, 1],
        [-1, 1, 1],
        [1, -1, 1]
    ])
    
    quarks = ["Up", "Charm", "Top", "Down", "Strange", "Bottom"]
    up_types = ["Up", "Charm", "Top"]
    down_types = ["Down", "Strange", "Bottom"]
    
    # Pre-extract vectors
    quark_vectors = {}
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
        vec = parse_vector(row['jones_polynomial_vector'])
        quark_vectors[qk] = vec

    # Scan n for q = exp(2pi i / n)
    # We'll test n from 3 to 120
    best_n = None
    max_matches = 0
    
    # Try both x = exp(i pi / n) and x = exp(2i pi / n)
    # convention: x = sqrt(t). If t = exp(2pi i / n), then x = exp(pi i / n).
    
    results_scan = []
    
    for n in range(3, 61):
        for x_mode in ['pi/n', '2pi/n']:
            if x_mode == 'pi/n':
                x_val = np.exp(1j * np.pi / n)
            else:
                x_val = np.exp(2j * np.pi / n)
                
            v_complex = np.zeros((3, 3), dtype=complex)
            for i, u in enumerate(up_types):
                for j, d in enumerate(down_types):
                    z_u = evaluate_at_x(quark_vectors[u], x_val)
                    z_d = evaluate_at_x(quark_vectors[d], x_val)
                    # Phase rule from Iter 8: Angle(Z_u - Z_d)
                    phase = np.angle(z_u - z_d)
                    v_complex[i, j] = np.exp(1j * phase)
            
            # Check sign matches with gauge transformation
            derived_signs = np.sign(np.real(v_complex))
            best_local_match = 0
            for r2 in [1, -1]:
                for r3 in [1, -1]:
                    for c1 in [1, -1]:
                        for c2 in [1, -1]:
                            for c3 in [1, -1]:
                                transform = np.array([
                                    [1 * c1, 1 * c2, 1 * c3],
                                    [r2 * c1, r2 * c2, r2 * c3],
                                    [r3 * c1, r3 * c2, r3 * c3]
                                ])
                                match = np.sum((derived_signs * transform) == target_signs)
                                if match > best_local_match:
                                    best_local_match = match
            
            if best_local_match > max_matches:
                max_matches = best_local_match
                best_n = (n, x_mode)
            
            if best_local_match == 9:
                results_scan.append({'n': n, 'mode': x_mode, 'match': int(best_local_match)})

    print(f"Best n found: {best_n} with {max_matches}/9 matches")
    print(f"Perfect matches: {results_scan}")

if __name__ == "__main__":
    main()
