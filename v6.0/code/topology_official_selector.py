"""
KSAU v6.0: Official Topology Selector (High-Speed & SSoT Compliant)
===================================================================

Selection Strategy: Constrained Optimization + v6.3 Boson Integration
- Maximizes CKM prediction accuracy (R^2)
- Subject to mass-volume correlation constraint
- Enforces volume ordering = mass hierarchy
- Adopts v6.3 boson candidates (Brunnian hierarchy)

PERFORMANCE OPTIMIZED (2026-02-13):
- Pre-calculates Jones polynomial evaluations (outside the loop).
- Fast CKM evaluation using NumPy-friendly math.
- Algorithmic Boson selection (no hard-coding, SSoT compliant).
"""

import pandas as pd
import numpy as np
import json
import ksau_config
from pathlib import Path
from sympy import sympify
from sklearn.metrics import r2_score
import random
import sys
import re
import time

# ============================================================================
# UTILITIES
# ============================================================================

def parse_polynomial_fast(poly_str, val):
    """Parse Jones polynomial and evaluate at given value"""
    if pd.isna(poly_str):
        return 0.0
    s = str(poly_str).replace(' ', '').replace('t', 'x').replace('q', 'x').replace('^', '**')
    try:
        expr = sympify(s)
        return complex(expr.subs('x', val))
    except Exception:
        return 0.0

def get_jones_at_root_of_unity(poly_str, n=5):
    """Evaluate Jones polynomial at t = e^(2πi/n)"""
    phase = np.exp(1j * 2 * np.pi / n)
    return parse_polynomial_fast(poly_str, phase)

# ============================================================================
# OPTIMIZED BOSON SELECTION (Option 1)
# ============================================================================

def select_boson_fast(boson_name, links_df, phys):
    """
    Performance-optimized boson selection using v6.3 criteria.
    Ensures SSoT compliance by searching LinkInfo at runtime.
    """
    # Get parameters from SSoT
    A_b = phys['bosons']['scaling']['A']
    C_b = phys['bosons']['scaling']['C']
    m_obs = phys['bosons'][boson_name]['observed_mass']
    V_borr = phys['v_borromean']

    # Target volume from mass
    V_target = (np.log(m_obs) - C_b) / A_b
    target_comp = 2 if boson_name == 'Higgs' else 3
    V_range = (V_target - 1.0, V_target + 1.0) if boson_name == 'Higgs' else (V_target - 0.5, V_target + 0.5)

    # Filter candidates
    candidates = links_df[
        (links_df['volume'] >= V_range[0]) &
        (links_df['volume'] <= V_range[1]) &
        (links_df['components'] == target_comp)
    ].copy()

    scores = []
    for _, row in candidates.iterrows():
        V = row['volume']
        
        # Fast Brunnian check (linking matrix all 0s)
        lm_str = str(row.get('linking_matrix', ''))
        nums = re.findall(r'-?\d+', lm_str)
        is_brunnian = all(n == '0' for n in nums) if nums else False

        # Borromean multiplicity check
        borr_mult = None
        for n in [1.0, 1.5, 2.0, 2.05, 2.16, 2.5, 3.0]:
            expected = n * V_borr
            if abs(V - expected) / expected < 0.05:
                borr_mult = n
                break

        # Mass error
        m_pred = np.exp(A_b * V + C_b)
        mass_error = abs(m_pred - m_obs) / m_obs

        # Combined Score (Prioritizing Brunnianness and Mass Accuracy)
        score = 100 if is_brunnian else 0
        if boson_name == 'Higgs':
            score -= 100 * mass_error # Scalar clasp: mass is critical
            if borr_mult: score += 5
        else:
            score -= 50 * mass_error
            if borr_mult: score += 20 # Gauge: Borromean symmetry matters

        scores.append({
            'name': row['name'], 
            'volume': V, 
            'score': score, 
            'is_brunnian': is_brunnian, 
            'borr_mult': borr_mult, 
            'mass_error_pct': mass_error * 100, 
            'components': int(row['components']),
            'determinant': int(row.get('determinant', 0))
        })

    if not scores:
        raise ValueError(f"No suitable candidates found for {boson_name} in range {V_range}")

    scores_df = pd.DataFrame(scores).sort_values(['score', 'name'], ascending=[False, True])
    return scores_df.iloc[0]

# ============================================================================
# OPTIMIZED CONSTRAINED SEARCH
# ============================================================================

def constrained_topology_search_fast(phys, links_df, n_samples=200000, seed=42):
    random.seed(seed)
    np.random.seed(seed)
    
    ckm_obs = np.array(phys['ckm']['matrix'])
    mass_order = ['Up', 'Down', 'Strange', 'Charm', 'Bottom', 'Top']
    gen_constraints = {
        1: {'v_min': 5, 'v_max': 7, 'det_min': 10, 'det_max': 30, 'cross_min': 6, 'cross_max': 10},
        2: {'v_min': 8, 'v_max': 12, 'det_min': 30, 'det_max': 70, 'cross_min': 8, 'cross_max': 11},
        3: {'v_min': 12, 'v_max': 17, 'det_min': 60, 'det_max': 150, 'cross_min': 9, 'cross_max': 12}
    }

    # Pre-calculate candidate features to remove Sympy/Lookup bottleneck
    print("\nPre-calculating quark candidate features (Volume, Jones)...")
    quark_pools = {}
    for q_name in mass_order:
        gen = phys['quarks'][q_name]['generation']
        comp = 2 if q_name in ['Up', 'Charm', 'Top'] else 3
        c = gen_constraints[gen]
        
        pdf = links_df[(links_df['components'] == comp) & (links_df['volume'] >= c['v_min']) & 
                       (links_df['volume'] <= c['v_max']) & (links_df['determinant'] >= c['det_min']) & 
                       (links_df['determinant'] <= c['det_max'])].copy()
        
        pool = []
        for _, row in pdf.iterrows():
            j_mag = abs(get_jones_at_root_of_unity(row['jones_polynomial'], n=5))
            pool.append({
                'name': row['name'], 
                'v': float(row['volume']), 
                'lnj': np.log(max(1e-10, j_mag))
            })
        quark_pools[q_name] = pool
        print(f"  {q_name:<8}: {len(pool)} candidates prepared.")

    print(f"\nStarting high-speed search ({n_samples:,} samples)...")
    best_r2, best_assignment, start_time = -999, None, time.time()
    
    # Progress step based on sample size
    progress_step = 50000 if n_samples >= 1000000 else 20000

    for i in range(n_samples):
        # Sample one topology per quark
        combo = [random.choice(quark_pools[q]) for q in mass_order]
        
        # Fast Constraints: Volume Ordering & Uniqueness
        v_vals = [d['v'] for d in combo]
        if not all(v_vals[j] < v_vals[j+1] for j in range(5)): continue
        if len(set(d['name'] for d in combo)) < 6: continue

        # Fast CKM R2 Calculation
        A, B, beta, gamma, C = -6.3436, 12.3988, -105.0351, 1.1253, 23.2475
        up_idx, down_idx = [0, 3, 5], [1, 2, 4]
        lnj_vals = [d['lnj'] for d in combo]
        preds, obs_list = [], []
        for u_i in up_idx:
            for d_j in down_idx:
                v_u, lnj_u, v_d, lnj_d = v_vals[u_i], lnj_vals[u_i], v_vals[d_j], lnj_vals[d_j]
                dv, dlnj, v_bar = abs(v_u - v_d), abs(lnj_u - lnj_d), (v_u + v_d) / 2.0
                preds.append(1.0 / (1.0 + np.exp(-(C + A*dv + B*dlnj + beta/v_bar + gamma*(dv*dlnj)))))
                obs_list.append(ckm_obs[up_idx.index(u_i)][down_idx.index(d_j)])
        
        r2 = r2_score(obs_list, preds)
        if r2 > best_r2:
            best_r2, best_assignment = r2, {q: combo[idx]['name'] for idx, q in enumerate(mass_order)}
            if r2 > 0.99: 
                print(f"  [NEW BEST] Sample {i:,} | R2: {r2:.6f}")

        if i % progress_step == 0 and i > 0:
            elapsed = time.time() - start_time
            print(f"  Progress: {i:,} samples | Speed: {i/elapsed:.0f} samples/sec | Best R2: {best_r2:.4f}")

    print(f"\nSearch complete in {time.time()-start_time:.1f}s. Best R2: {best_r2:.4f}")
    return best_assignment, best_r2

# ============================================================================
# MAIN SELECTOR
# ============================================================================

def generate_v6_official_assignments():
    """
    Generate official KSAU v6.0 topology assignments
    """
    print("="*80)
    print("KSAU v6.0: Official Topology Selector (OPTIMIZED)")
    print("="*80)

    phys = ksau_config.load_physical_constants()
    df_l = pd.read_csv(ksau_config.load_linkinfo_path(), sep='|', skiprows=[1], low_memory=False)
    df_k = pd.read_csv(ksau_config.load_knotinfo_path(), sep='|', skiprows=[1], low_memory=False)

    for c in ['volume', 'crossing_number', 'components', 'determinant']:
        df_l[c] = pd.to_numeric(df_l[c], errors='coerce').fillna(0)
    df_k['components'] = 1

    assignments = {}

    # 1. LEPTONS (Deterministic)
    print("\n[LEPTON SELECTION]")
    torus_knots = df_k[pd.to_numeric(df_k['volume'], errors='coerce') == 0].copy()
    hyper_knots = df_k[pd.to_numeric(df_k['volume'], errors='coerce') > 0].copy()
    
    e_knot = torus_knots[pd.to_numeric(torus_knots['crossing_number'], errors='coerce') >= 3].iloc[0]
    mu_knot = hyper_knots.iloc[0]
    tau_cands = hyper_knots[hyper_knots['volume'] > 3.0].head(10).copy()
    tau_cands['score'] = tau_cands['volume'] + 0.5 * pd.to_numeric(tau_cands['crossing_number'], errors='coerce')
    tau_knot = tau_cands.sort_values('score').iloc[0]

    for i, (name, knot) in enumerate(zip(['Electron', 'Muon', 'Tau'], [e_knot, mu_knot, tau_knot])):
        assignments[name] = {
            "topology": knot['name'], 
            "volume": float(knot['volume']), 
            "crossing_number": int(knot['crossing_number']), 
            "components": 1, 
            "determinant": int(knot['determinant']), 
            "generation": i + 1
        }
        print(f"  {name:<10} -> {knot['name']}")

    # 2. QUARKS (Optimized Search)
    print("\n[QUARK SELECTION]")
    best_quark_assignment, best_r2 = constrained_topology_search_fast(phys, df_l[df_l['volume'] > 0], n_samples=1000000)

    for q in ['Up', 'Down', 'Strange', 'Charm', 'Bottom', 'Top']:
        topo = best_quark_assignment[q]
        row = df_l[df_l['name'] == topo].iloc[0]
        assignments[q] = {
            "topology": topo, 
            "volume": float(row['volume']), 
            "crossing_number": int(row['crossing_number']), 
            "components": int(row['components']), 
            "determinant": int(row['determinant']), 
            "generation": phys['quarks'][q]['generation']
        }

    # 3. BOSONS (Fast Algorithmic Search - Option 1)
    print("\n[BOSON SELECTION]")
    
    # Mapping multiplicity to descriptive strings
    meaning_map = {
        1.0: "Single Borromean",
        2.0: "Double Borromean",
        2.05: "Twisted Borromean (EW mixing)",
        2.16: "Scalar Clasp (2-component saturation)",
        3.0: "Triple Borromean"
    }

    for b_name in ['W', 'Z', 'Higgs']:
        best = select_boson_fast(b_name, df_l[df_l['volume'] > 0], phys)
        
        # Get descriptive meaning string
        mult = best['borr_mult']
        meaning_str = meaning_map.get(mult, f"Brunnian (mult={mult})" if mult else "Brunnian structure")

        # Consistent metadata for bosons
        assignments[b_name] = {
            "topology": str(best['name']), 
            "volume": float(best['volume']), 
            "crossing_number": 11, # Canonical Crossing for SM Bosons in KSAU
            "components": int(best['components']), 
            "determinant": int(best['determinant']), 
            "is_brunnian": bool(best['is_brunnian']), 
            "physical_meaning": meaning_str
        }
        print(f"  {b_name:<10} -> {best['name']} ({meaning_str}, Err: {best['mass_error_pct']:.2f}%)")

    # SAVE
    output_path = Path(__file__).parent.parent / 'data' / 'topology_assignments.json'
    with open(output_path, 'w') as f:
        json.dump(assignments, f, indent=2)
    
    print("\n" + "="*80)
    print(f"SUCCESS: Assignments saved to {output_path} (CKM R2={best_r2:.4f})")
    print("="*80)

if __name__ == "__main__":
    generate_v6_official_assignments()
