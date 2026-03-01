
import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd
import re

# Setup SSOT
current_file = Path(__file__).resolve()
# Based on the prompt: project_root = current_file.parents[5]
# But iter_01 is at cycles/cycle_26/iterations/iter_01/code/eval.py
# parents[0] = code
# parents[1] = iter_01
# parents[2] = iterations
# parents[3] = cycle_26
# parents[4] = cycles
# parents[5] = KSAU_Project
project_root = current_file.parents[5]
ssot_path = project_root / "ssot"
sys.path.insert(0, str(ssot_path))    
from ksau_ssot import SSOT

def parse_vector(vec_str):
    if not isinstance(vec_str, str) or pd.isna(vec_str):
        return None
    # Remove [] or {}
    clean_str = vec_str.strip('[]{}')
    # Split by comma
    parts = re.split(r',\s*', clean_str)
    try:
        nums = [int(p) for p in parts]
        if len(nums) < 2:
            return None
        min_pow = nums[0]
        max_pow = nums[1]
        coeffs = nums[2:]
        return min_pow, max_pow, coeffs
    except ValueError:
        return None

def evaluate_jones(vector, q):
    if vector is None:
        return None
    min_pow, max_pow, coeffs = vector
    val = 0j
    for i, c in enumerate(coeffs):
        p = min_pow + i
        # For knots, p is power of t. For links, p is power of x.
        # We assume x = q^(1/2). So x^p = q^(p/2).
        # Actually, let's treat knots as having 1 component, so x^p = q^(p/2) with p even?
        # No, the vector for knots uses t. 
        # Let's check the convention.
        # If LinkInfo uses x = t^(1/2), then KnotInfo using t^k is the same as x^(2k).
        # But KnotInfo vectors use powers of t.
        # So val += c * (q ** p) for knots?
        # Let's look at L2a1{1}: Jones -x-x^5. Vector {1, 5, -1, 0, 0, 0, -1}.
        # This is definitely in x.
        # So for links, val += c * (q ** (p/2.0)).
        # For knots, the vector is in t. val += c * (q ** p).
        pass
    
    # Let's check if we can distinguish knots and links by the string brackets or something.
    # Actually, knots have 1 component. Links have > 1.
    return None # Placeholder

def main():
    ssot = SSOT()
    consts = ssot.constants()
    knots_df, links_df = ssot.knot_data()
    topo_assignments = ssot.topology_assignments()
    
    q_val = np.exp(2j * np.pi / 24)
    
    quarks = ["Up", "Charm", "Top", "Down", "Strange", "Bottom"]
    results = {}
    
    for qk in quarks:
        topo_name = topo_assignments[qk]["topology"]
        # Find in knots or links
        row = knots_df[knots_df['name'] == topo_name]
        is_link = False
        if row.empty:
            row = links_df[links_df['name'] == topo_name]
            is_link = True
        
        if row.empty:
            print(f"Warning: {topo_name} not found for {qk}")
            continue
            
        vec_str = row.iloc[0]['jones_polynomial_vector']
        vector = parse_vector(vec_str)
        
        if vector:
            min_pow, max_pow, coeffs = vector
            val = 0j
            for i, c in enumerate(coeffs):
                p = min_pow + i
                if is_link:
                    # LinkInfo Jones is in x = t^(1/2). 
                    # If t = q, then x = q^(1/2).
                    val += c * (q_val ** (p / 2.0))
                else:
                    # KnotInfo Jones is in t.
                    val += c * (q_val ** p)
            
            results[qk] = {
                "topology": topo_name,
                "value": {"real": val.real, "imag": val.imag},
                "phase": np.angle(val),
                "magnitude": np.abs(val)
            }
        else:
            print(f"Warning: No Jones vector for {topo_name}")

    # Compute CKM signs
    # 3x3 matrix
    up_types = ["Up", "Charm", "Top"]
    down_types = ["Down", "Strange", "Bottom"]
    ckm_signs = np.zeros((3, 3))
    
    # We need a rule to combine them. 
    # Let's try: Sign(V_ij) = sign(Re(V_up * conj(V_down)))
    # Or maybe sign(cos(phase_up - phase_down))
    
    analysis_results = []
    for i, u in enumerate(up_types):
        row_signs = []
        for j, d in enumerate(down_types):
            if u in results and d in results:
                v_u = results[u]["value"]["real"] + 1j * results[u]["value"]["imag"]
                v_d = results[d]["value"]["real"] + 1j * results[d]["value"]["imag"]
                
                # Evaluation point resonance check
                # H67 says Jones phase extraction.
                # Let's try the phase difference.
                phase_diff = np.angle(v_u * np.conj(v_d))
                sign = np.sign(np.cos(phase_diff))
                row_signs.append(int(sign))
                
                analysis_results.append({
                    "u": u, "d": d,
                    "phase_u": results[u]["phase"],
                    "phase_d": results[d]["phase"],
                    "phase_diff": phase_diff,
                    "cos_phase_diff": np.cos(phase_diff),
                    "derived_sign": int(sign)
                })
            else:
                row_signs.append(0)
        ckm_signs[i] = row_signs

    output = {
        "q_evaluation_point": "exp(2pi i / 24)",
        "quark_results": results,
        "ckm_sign_matrix": ckm_signs.tolist(),
        "analysis": analysis_results
    }
    
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
