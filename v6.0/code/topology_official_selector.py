import pandas as pd
import numpy as np
import json
import ksau_config
from pathlib import Path
from sklearn.linear_model import LinearRegression
import re
from sympy import sympify
import itertools

# ============================================================================
# UTILITIES
# ============================================================================

def parse_polynomial(poly_str, val):
    if pd.isna(poly_str): return 0.0
    s = str(poly_str).replace(' ', '').replace('t', 'x').replace('q', 'x').replace('^', '**')
    try:
        expr = sympify(s)
        return complex(expr.subs('x', val))
    except Exception:
        return 0.0

def get_jones_mag(poly_str):
    phase = np.exp(1j * 2 * np.pi / 5)
    val = parse_polynomial(poly_str, phase)
    return abs(val)

# ============================================================================
# OPTIMIZATION ENGINES
# ============================================================================

def calculate_ckm_score_v2(combination, ckm_exp):
    up_types = ['Up', 'Charm', 'Top']
    down_types = ['Down', 'Strange', 'Bottom']
    X, y = [], []
    for i, u in enumerate(up_types):
        for j, d in enumerate(down_types):
            dV = abs(combination[u]['V'] - combination[d]['V'])
            dlnJ = abs(combination[u]['lnJ'] - combination[d]['lnJ'])
            v_bar = (combination[u]['V'] + combination[d]['V']) / 2.0
            p_obs = np.clip(ckm_exp[i, j], 1e-6, 1.0 - 1e-6)
            logit_p = np.log(p_obs / (1.0 - p_obs))
            target = logit_p + 0.5 * dV
            X.append([dlnJ, 1.0 / v_bar])
            y.append(target)
    reg = LinearRegression().fit(X, y)
    preds_z = -0.5 * np.array([abs(combination[u]['V'] - combination[d]['V']) for u in up_types for d in down_types]) + reg.predict(X)
    p_true_clipped = np.clip(ckm_exp.flatten(), 1e-6, 1.0 - 1e-6)
    y_true_logit = np.log(p_true_clipped / (1.0 - p_true_clipped))
    r2_global = 1 - (np.sum((y_true_logit - preds_z)**2) / np.sum((y_true_logit - np.mean(y_true_logit))**2))
    return r2_global

def generate_v6_official_assignments():
    print("="*80)
    print("KSAU v6.0: Dynamical Global Optimization (Logit-Geometric + Crossing Scan)")
    print("Status: Deriving Topologies from Explicit Boundary Ansatz")
    print("="*80)
    
    # Load Constants and Ansatz
    phys = ksau_config.load_physical_constants()
    ansatz = phys.get('boundary_ansatz', {})
    cl_intercept = ansatz.get('cl_intercept', -2.38)
    range_min, range_max = ansatz.get('scan_range', [3, 12])
    
    coeffs = ksau_config.get_kappa_coeffs()
    kappa = ksau_config.KAPPA
    
    # Load Databases
    df_l = pd.read_csv(ksau_config.load_linkinfo_path(), sep='|', skiprows=[1])
    for c in ['volume', 'crossing_number', 'components', 'determinant']:
        df_l[c] = pd.to_numeric(df_l[c], errors='coerce').fillna(0)
    
    df_k = pd.read_csv(ksau_config.load_knotinfo_path(), sep='|', skiprows=[1], low_memory=False)
    df_k['crossing_number'] = pd.to_numeric(df_k['crossing_number'], errors='coerce').fillna(0)
    df_k['determinant'] = pd.to_numeric(df_k['determinant'], errors='coerce').fillna(0)

    # 1. Quarks: Optimal CKM + Mass Fit
    print(f"Phase 1: Optimizing Quarks (CKM Global Fit)...")
    ckm_exp = np.array(phys['ckm']['matrix'])
    quark_candidates = {}
    for q_name, q_meta in phys['quarks'].items():
        comp = 2 if q_name in ['Up', 'Charm', 'Top'] else 3
        twist = (2 - q_meta['generation']) * ((-1)**comp)
        target_v = (np.log(q_meta['observed_mass']) - kappa*twist - coeffs['quark_intercept']) / coeffs['quark_vol_coeff']
        
        subset = df_l[(df_l['components'] == comp) & (df_l['crossing_number'] <= 12)].copy()
        subset['vol_diff'] = (subset['volume'] - target_v).abs()
        cands = subset.sort_values('vol_diff').head(5)
        quark_candidates[q_name] = [{'name': r['name'], 'V': r['volume'], 'lnJ': np.log(max(1e-10, get_jones_mag(r['jones_polynomial']))), 'det': r['determinant'], 'crossing': r['crossing_number'], 'comp': r['components']} for _, r in cands.iterrows()]

    best_score, best_set = -1, None
    for c in quark_candidates['Charm']:
      for s in quark_candidates['Strange']:
        for b in quark_candidates['Bottom']:
          for t in quark_candidates['Top']:
            comb = {'Up': quark_candidates['Up'][0], 'Down': quark_candidates['Down'][0], 'Charm': c, 'Strange': s, 'Bottom': b, 'Top': t}
            r2 = calculate_ckm_score_v2(comb, ckm_exp)
            if r2 > best_score: best_score, best_set = r2, comb

    print(f"  Quark Fit Complete. Best CKM R^2: {best_score:.4f}")
    
    assignments = {}
    for q in best_set:
        assignments[q] = {"topology": best_set[q]['name'], "volume": best_set[q]['V'], "crossing_number": int(best_set[q]['crossing']), "components": int(best_set[q]['comp']), "determinant": int(best_set[q]['det']), "generation": phys['quarks'][q]['generation']}

    # 2. Leptons: Boundary Principle Scan
    print(f"\nPhase 2: Scanning Crossing Sequences [N_min={range_min}, N_max={range_max}]...")
    # Pre-filter Canonical Knots
    canonical_knots = {}
    for n in range(range_min, range_max + 1):
        subset = df_k[df_k['crossing_number'] == n].copy()
        if not subset.empty:
            canonical_knots[n] = subset.sort_values('determinant').iloc[0]

    # Evaluate all possible sequences
    results = []
    possible_n = sorted(canonical_knots.keys())
    slope_l = coeffs['lepton_n2_coeff']
    
    for seq in itertools.combinations(possible_n, 3):
        mae_sum = 0
        for i, l_name in enumerate(['Electron', 'Muon', 'Tau']):
            n = seq[i]
            knot = canonical_knots[n]
            obs = phys['leptons'][l_name]['observed_mass']
            twist = (i + 1) - 2
            det = int(knot['determinant'])
            log_pred = slope_l * (n**2) + kappa * twist - kappa * np.log(det) + cl_intercept
            mae_sum += abs(np.exp(log_pred) - obs) / obs
        results.append({'seq': seq, 'mae': mae_sum / 3.0})

    results.sort(key=lambda x: x['mae'])
    
    print("\nTop 5 Discovered Sequences:")
    for i, res in enumerate(results[:5]):
        mark = " (Winner)" if i == 0 else ""
        print(f"  {i+1}. N={res['seq']} -> MAE: {res['mae']*100:.2f}%{mark}")

    best_seq = results[0]['seq']
    for i, l_name in enumerate(['Electron', 'Muon', 'Tau']):
        n = best_seq[i]
        knot = canonical_knots[n]
        assignments[l_name] = {"topology": knot['name'], "volume": 0.0, "crossing_number": int(knot['crossing_number']), "components": 1, "determinant": int(knot['determinant']), "generation": i + 1}
        print(f"  Final Assignment: {l_name:<8} -> {knot['name']} (N={n}, Det={knot['determinant']})")

    # 3. Bosons
    print("\nPhase 3: Discovering Boson Topologies (Brunnian Restriction)...")
    for b_name, b_meta in phys['bosons'].items():
        if b_name == 'scaling': continue
        br_req = b_meta['is_brunnian_required']
        subset = df_l[df_l['crossing_number'] <= 12].copy()
        if br_req: subset = subset[subset['name'].str.contains('n')]
        subset['v_diff'] = (subset['volume'] - 15.0).abs() # Standard gauge target
        best_link = subset.sort_values('v_diff').iloc[0]
        topo_name = f"{best_link['name']}{{0,0,0}}" if best_link['components'] == 3 else f"{best_link['name']}{{0,0}}"
        assignments[b_name] = {"topology": topo_name, "volume": float(best_link['volume']), "crossing_number": int(best_link['crossing_number']), "components": int(best_link['components']), "determinant": int(best_link['determinant']), "is_brunnian": br_req}
        print(f"  Final Assignment: {b_name:<8} -> {topo_name} (Brunnian={br_req})")

    output_path = Path('v6.0/data/topology_assignments.json')
    with open(output_path, 'w') as f: json.dump(assignments, f, indent=2)
    print(f"\nSuccess: Assignments fully discovered from Boundary Ansatz and saved to {output_path}")

if __name__ == "__main__":
    generate_v6_official_assignments()
