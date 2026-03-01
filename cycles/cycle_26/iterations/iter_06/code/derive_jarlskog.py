
import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd
import re

# Setup SSOT
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
ssot_path = project_root / "ssot"
sys.path.insert(0, str(ssot_path))    
from ksau_ssot import SSOT

def parse_vector(vec_str):
    if not isinstance(vec_str, str) or pd.isna(vec_str):
        return None
    clean_str = vec_str.strip('[]{}')
    parts = re.split(r',\s*', clean_str)
    try:
        nums = [int(p) for p in parts]
        if len(nums) < 2: return None
        min_pow, max_pow, coeffs = nums[0], nums[1], nums[2:]
        return min_pow, max_pow, coeffs
    except ValueError:
        return None

def evaluate_jones_at_q(vector, q_val, is_link):
    if vector is None: return 0j
    min_pow, max_pow, coeffs = vector
    val = 0j
    for i, c in enumerate(coeffs):
        p = min_pow + i
        if is_link:
            val += c * (q_val ** (p / 2.0))
        else:
            val += c * (q_val ** p)
    return val

def get_jarlskog_invariant(v):
    # J = Im(V_11 V_22 V_12* V_21*)
    return np.imag(v[0, 0] * v[1, 1] * np.conj(v[0, 1]) * np.conj(v[1, 0]))

def main():
    ssot = SSOT()
    consts = ssot.constants()
    knots_df, links_df = ssot.knot_data()
    topo_assignments = ssot.topology_assignments()
    
    # Target values
    ckm_mags = np.array(consts['ckm_matrix']['V_ij'])
    target_j = consts['cp_violation']['jarlskog_J']
    
    q_val = np.exp(2j * np.pi / 24)
    
    # 1. Evaluate Jones values (Z) for all quarks
    quarks = ["Up", "Charm", "Top", "Down", "Strange", "Bottom"]
    quark_z = {}
    for qk in quarks:
        topo_name = topo_assignments[qk]["topology"]
        row = knots_df[knots_df['name'] == topo_name]
        is_link = False
        if row.empty:
            row = links_df[links_df['name'] == topo_name]
            is_link = True
        
        if row.empty: raise ValueError(f"Topology {topo_name} not found.")
            
        vec_str = row.iloc[0]['jones_polynomial_vector']
        vector = parse_vector(vec_str)
        val = evaluate_jones_at_q(vector, q_val, is_link)
        quark_z[qk] = val
        print(f"{qk:7}: {val.real:10.4f} + {val.imag:10.4f}i")

    up_types = ["Up", "Charm", "Top"]
    down_types = ["Down", "Strange", "Bottom"]
    
    z_up = [quark_z[u] for u in up_types]
    z_down = [quark_z[d] for d in down_types]
    
    # 2. Test Rule: Phase(V_ij) = Arg(Z_up_i - Z_down_j)
    v_complex = np.zeros((3, 3), dtype=complex)
    for i in range(3):
        for j in range(3):
            phase = np.angle(z_up[i] - z_down[j])
            v_complex[i, j] = ckm_mags[i, j] * np.exp(1j * phase)
    
    j_derived = get_jarlskog_invariant(v_complex)
    
    # 3. Test Rule: Phase(V_ij) = Arg(Z_up_i / Z_down_j + constant?) 
    # Let's just stick to the difference for now as it's the most promising for J != 0
    
    print(f"Target J:  {target_j:.4e}")
    print(f"Derived J: {j_derived:.4e}")
    print(f"Error %:   {abs(j_derived - target_j)/target_j*100:.2f}%")

    results = {
        "iteration": 6,
        "hypothesis_id": "H67",
        "q_val": "exp(2pi i / 24)",
        "quark_z_values": {k: {"real": v.real, "imag": v.imag} for k, v in quark_z.items()},
        "model": "Phase(V_ij) = Arg(Z_up_i - Z_down_j)",
        "assigned_j": float(j_derived),
        "target_j": float(target_j),
        "j_error_pct": float(abs(j_derived - target_j) / target_j * 100)
    }
    
    with open(current_file.parents[1] / "results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
