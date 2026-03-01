
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
    if not isinstance(vec_str, str) or pd.isna(vec_str): return None
    clean_str = vec_str.strip('[]{}')
    parts = re.split(r',\s*', clean_str)
    try:
        nums = [int(p) for p in parts]
        if len(nums) < 2: return None
        return nums[0], nums[1], nums[2:]
    except: return None

def evaluate_jones_at_q(vector, q_val, is_link):
    if vector is None: return 0j
    min_pow, max_pow, coeffs = vector
    val = 0j
    for i, c in enumerate(coeffs):
        p = min_pow + i
        if is_link: val += c * (q_val ** (p / 2.0))
        else: val += c * (q_val ** p)
    return val

def bloch_wigner(z):
    """Bloch-Wigner dilogarithm function D(z)"""
    if abs(z) < 1e-15 or abs(z - 1.0) < 1e-15: return 0.0
    from scipy.special import spence
    # Li2(z) in scipy is spence(1-z)
    # D(z) = Im(Li2(z)) + arg(1-z) * log|z|
    # Note: spence(z) = sum (1-z)^n/n^2. 
    # Li2(z) = spence(1-z)
    li2 = spence(1-z)
    return np.imag(li2) + np.angle(1-z) * np.log(abs(z))

def main():
    ssot = SSOT()
    consts = ssot.constants()
    knots_df, links_df = ssot.knot_data()
    topo_assignments = ssot.topology_assignments()
    
    target_j = consts['cp_violation']['jarlskog_J']
    q_val = np.exp(2j * np.pi / 24)
    kappa = consts['mathematical_constants']['kappa']
    
    # 1. Evaluate Z for all quarks
    quarks = ["Up", "Charm", "Top", "Down", "Strange", "Bottom"]
    quark_z = {}
    for qk in quarks:
        topo_name = topo_assignments[qk]["topology"]
        row = knots_df[knots_df['name'] == topo_name]
        is_link = False
        if row.empty:
            row = links_df[links_df['name'] == topo_name]
            is_link = True
        vec_str = row.iloc[0]['jones_polynomial_vector']
        quark_z[qk] = evaluate_jones_at_q(parse_vector(vec_str), q_val, is_link)

    # 2. Calculate Cross Ratio for 1st and 2nd generation
    # z = (U1-D1)(U2-D2) / (U1-D2)(U2-D1)
    u1, u2 = quark_z["Up"], quark_z["Charm"]
    d1, d2 = quark_z["Down"], quark_z["Strange"]
    
    z = ((u1 - d1) * (u2 - d2)) / ((u1 - d2) * (u2 - d1))
    
    d_z = bloch_wigner(z)
    
    # Hypothesis: J is proportional to D(z)
    # J = area of unitary triangle. 
    # Maybe J = kappa^k * D(z)?
    
    print(f"Cross Ratio z: {z}")
    print(f"D(z):          {d_z:.6f}")
    
    # Try scaling
    # We saw J ~ kappa^5
    j_est = abs(d_z) * (kappa ** 4) # Trial 1
    print(f"Est J (kappa^4 * |D(z)|): {j_est:.4e}")
    
    j_est2 = abs(d_z) * (kappa ** 5) # Trial 2
    print(f"Est J (kappa^5 * |D(z)|): {j_est2:.4e}")

    # What if J = Im(z)?
    print(f"Im(z): {z.imag:.4e}")
    
    # Save results
    results = {
        "iteration": 6,
        "hypothesis_id": "H67",
        "cross_ratio_z": {"real": z.real, "imag": z.imag},
        "bloch_wigner_d_z": d_z,
        "target_j": target_j,
        "kappa": kappa
    }
    with open(current_file.parents[1] / "results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
