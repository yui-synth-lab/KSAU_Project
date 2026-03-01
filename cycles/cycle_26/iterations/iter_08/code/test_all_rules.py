
import numpy as np
import pandas as pd
import sys
from pathlib import Path
import re
import json
from scipy.special import spence

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

def check_signs_detail(v_complex_matrix, target_signs, up_types, down_types):
    derived_signs = np.sign(np.real(v_complex_matrix))
    best_match = 0
    best_trial = None
    for r2 in [1, -1]:
        for r3 in [1, -1]:
            for c1 in [1, -1]:
                for c2 in [1, -1]:
                    for c3 in [1, -1]:
                        transform = np.array([[1*c1, 1*c2, 1*c3], [r2*c1, r2*c2, r2*c3], [r3*c1, r3*c2, r3*c3]])
                        trial_signs = derived_signs * transform
                        match = np.sum(trial_signs == target_signs)
                        if match > best_match: 
                            best_match = match
                            best_trial = trial_signs
    
    mismatches = []
    if best_match < 9:
        for i in range(3):
            for j in range(3):
                if best_trial[i, j] != target_signs[i, j]:
                    mismatches.append(f"{up_types[i]}-{down_types[j]}")
    return best_match, mismatches

def main():
    ssot = SSOT()
    consts = ssot.constants()
    knots_df, links_df = ssot.knot_data()
    topo_assignments = ssot.topology_assignments()
    
    pi = consts['mathematical_constants']['pi']
    alpha_inv = 1.0 / consts['physical_constants']['alpha_em']
    sin2w = consts['physical_constants']['sin2theta_w']
    d_bulk = consts['dimensions']['bulk_total']
    
    A_geo = -2 * pi
    B_geo = 4 * pi
    beta_geo = -alpha_inv * (1 - sin2w)
    gamma_geo = 9.0 / 8.0
    C_geo = np.exp(pi) + (1.0 / d_bulk)
    
    quarks = ["Up", "Charm", "Top", "Down", "Strange", "Bottom"]
    quark_data = {}
    x_mag = np.exp(2j * pi / 5)
    x_phase = np.exp(1j * pi / 24)
    
    for qk in quarks:
        name = topo_assignments[qk]['topology']
        row = links_df[links_df['name'] == name]
        if row.empty: row = knots_df[knots_df['name'] == name]
        if row.empty:
            base = name.split('{')[0]
            row = links_df[links_df['name'] == base]
            if row.empty: row = knots_df[knots_df['name'] == base]
            if row.empty: row = links_df[links_df['name'].str.startswith(base + "{")]
        row = row.iloc[0]
        vec = parse_vector(row['jones_polynomial_vector'])
        quark_data[qk] = {
            'V': float(row['volume']),
            'lnJ5': np.log(max(1e-10, abs(evaluate_at_x(vec, x_mag)))),
            'Z24': evaluate_at_x(vec, x_phase)
        }

    up_types = ["Up", "Charm", "Top"]
    down_types = ["Down", "Strange", "Bottom"]
    ckm_mags_exp = np.array(consts['ckm_matrix']['V_ij'])
    target_signs = np.array([[1, 1, 1], [-1, 1, 1], [1, -1, 1]])
    
    rules = {
        "Difference (Z_u - Z_d)": lambda u, d: u - d,
        "Ratio (Z_u / Z_d)": lambda u, d: u / d,
        "Product (Z_u * conj(Z_d))": lambda u, d: u * np.conj(d),
        "Mean Phase exp(i(phi_u-phi_d)/2)": lambda u, d: np.exp(0.5j * (np.angle(u) - np.angle(d))),
        "Sum (Z_u + Z_d)": lambda u, d: u + d
    }
    
    for rule_name, rule_func in rules.items():
        v_complex = np.zeros((3, 3), dtype=complex)
        for i, u in enumerate(up_types):
            for j, d in enumerate(down_types):
                ud, dd = quark_data[u], quark_data[d]
                dV, dlnJ = abs(ud['V'] - dd['V']), abs(ud['lnJ5'] - dd['lnJ5'])
                v_bar = (ud['V'] + dd['V']) / 2.0
                logit = C_geo + A_geo * dV + B_geo * dlnJ + beta_geo / v_bar + gamma_geo * (dV * dlnJ)
                mag = 1.0 / (1.0 + np.exp(-logit))
                v_complex[i, j] = mag * rule_func(ud['Z24'], dd['Z24'])
        
        match, misses = check_signs_detail(v_complex, target_signs, up_types, down_types)
        print(f"{rule_name:40}: {match}/9 matches. Misses: {misses}")

if __name__ == "__main__":
    main()
