
import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd
import re

# Setup SSOT
current_file = Path(__file__).resolve()
# parents[0] = code
# parents[1] = iter_02
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

def compute_ckm_complex(up_phases, down_phases, ckm_mags):
    """
    Construct complex CKM elements using phases from Jones poly: V_ij = |V_ij| * exp(i * (phi_u - phi_d))
    """
    v_complex = np.zeros((3, 3), dtype=complex)
    for i in range(3):
        for j in range(3):
            phase = up_phases[i] - down_phases[j]
            v_complex[i, j] = ckm_mags[i, j] * np.exp(1j * phase)
    return v_complex

def get_jarlskog(v):
    # J = Im(V_ud * V_cs * conj(V_us) * conj(V_cd))
    # Standard: J = Im(V_11 * V_22 * conj(V_12) * conj(V_21))
    return np.imag(v[0, 0] * v[1, 1] * np.conj(v[0, 1]) * np.conj(v[1, 2])) 
    # Actually, any combination like J = Im(V_ij V_kl V_il* V_kj*) for i!=k, j!=l

def get_jarlskog_invariant(v):
    # J is invariant regardless of which quartet we pick
    return np.imag(v[0, 0] * v[1, 1] * np.conj(v[0, 1]) * np.conj(v[1, 0]))

def main():
    ssot = SSOT()
    consts = ssot.constants()
    knots_df, links_df = ssot.knot_data()
    topo_assignments = ssot.topology_assignments()
    
    # Target CKM magnitudes from constants.json
    ckm_mags = np.array(consts['ckm_matrix']['V_ij'])
    target_j = consts['cp_violation']['jarlskog_J']
    
    q_val = np.exp(2j * np.pi / 24)
    
    # 1. Evaluate Jones phases for assigned topologies
    quarks = ["Up", "Charm", "Top", "Down", "Strange", "Bottom"]
    quark_info = {}
    for qk in quarks:
        topo_name = topo_assignments[qk]["topology"]
        row = knots_df[knots_df['name'] == topo_name]
        is_link = False
        if row.empty:
            row = links_df[links_df['name'] == topo_name]
            is_link = True
        
        if row.empty:
            raise ValueError(f"Topology {topo_name} not found.")
            
        vec_str = row.iloc[0]['jones_polynomial_vector']
        vector = parse_vector(vec_str)
        val = evaluate_jones_at_q(vector, q_val, is_link)
        quark_info[qk] = {"phase": np.angle(val), "topo": topo_name}

    up_types = ["Up", "Charm", "Top"]
    down_types = ["Down", "Strange", "Bottom"]
    
    assigned_up_phases = [quark_info[u]["phase"] for u in up_types]
    assigned_down_phases = [quark_info[d]["phase"] for d in down_types]
    
    v_assigned = compute_ckm_complex(assigned_up_phases, assigned_down_phases, ckm_mags)
    j_assigned = get_jarlskog_invariant(v_assigned)
    
    print(f"Assigned J: {j_assigned:.4e} (Target: {target_j:.4e})")

    # 2. Permutation Test
    # Pool all 6 topologies
    all_topo_names = [quark_info[q]["topo"] for q in quarks]
    all_phases = [quark_info[q]["phase"] for q in quarks]
    
    # Pre-calculated phases are in all_phases
    # Indices 0-5
    
    n_trials = 10000
    seed = 42
    rng = np.random.default_rng(seed)
    
    j_values = []
    
    # Null Hypothesis: The phase-topology assignment is random.
    # We permute the 6 phases among the 6 quark positions.
    for _ in range(n_trials):
        perm = rng.permutation(6)
        p_up = [all_phases[perm[0]], all_phases[perm[1]], all_phases[perm[2]]]
        p_down = [all_phases[perm[3]], all_phases[perm[4]], all_phases[perm[5]]]
        v_perm = compute_ckm_complex(p_up, p_down, ckm_mags)
        j_perm = get_jarlskog_invariant(v_perm)
        j_values.append(j_perm)
    
    j_values = np.array(j_values)
    
    # Two-tailed p-value: How often is |J_perm| >= |J_assigned|?
    p_val = np.sum(np.abs(j_values) >= np.abs(j_assigned)) / n_trials
    
    # Sign Match Rate Test
    # Target signs (Real part of V_ij in standard convention)
    # V ~ [+ + +; - + +; + - +]
    target_signs = np.array([
        [1, 1, 1],
        [-1, 1, 1],
        [1, -1, 1]
    ])
    
    def get_match_rate(v, target):
        v_signs = np.sign(np.real(v))
        return np.sum(v_signs == target) / 9.0

    match_assigned = get_match_rate(v_assigned, target_signs)
    
    match_rates = []
    for _ in range(n_trials):
        perm = rng.permutation(6)
        p_up = [all_phases[perm[0]], all_phases[perm[1]], all_phases[perm[2]]]
        p_down = [all_phases[perm[3]], all_phases[perm[4]], all_phases[perm[5]]]
        v_perm = compute_ckm_complex(p_up, p_down, ckm_mags)
        match_rates.append(get_match_rate(v_perm, target_signs))
    
    match_rates = np.array(match_rates)
    p_val_signs = np.sum(match_rates >= match_assigned) / n_trials

    results = {
        "iteration": 2,
        "hypothesis_id": "H67",
        "assigned_j": float(j_assigned),
        "target_j": float(target_j),
        "j_error_pct": float(abs(j_assigned - target_j) / target_j * 100),
        "j_p_value": float(p_val),
        "sign_match_rate_assigned": float(match_assigned),
        "sign_match_rate_p_value": float(p_val_signs),
        "monte_carlo_n": n_trials,
        "seed": seed
    }
    
    with open(current_file.parent.parent / "results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
