import pandas as pd
import numpy as np
import json
import ksau_config
from pathlib import Path
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
# TOPOLOGICAL FREEZE-OUT ENGINE
# ============================================================================

class FreezeOutSelector:
    def __init__(self, phys_consts):
        self.phys = phys_consts
        self.pi = np.pi
        self.alpha = phys_consts.get('alpha_em', 0.0072973525)
        geom = phys_consts['ckm']['geometric_coefficients']
        
        # Master Formula Constants (Loaded from Central Constants)
        self.A = geom['A_barrier_pi_factor'] * self.pi
        self.B = geom['B_complex_pi_factor'] * self.pi
        self.beta = geom['beta_visc_alpha_factor'] / self.alpha
        self.gamma = np.sqrt(geom['gamma_res_sqrt'])
        
        # C_drive is complex formula, we use the literal value or re-evaluate
        # For simplicity in this selector, we follow the formula from Paper IV
        self.C = (self.pi**2) + (2*self.pi)

    def calculate_logit(self, u_v, u_lnj, d_v, d_lnj):
        dV = abs(u_v - d_v)
        dlnJ = abs(u_lnj - d_lnj)
        v_bar = (u_v + d_v) / 2.0
        return self.C + self.A*dV + self.B*dlnJ + self.beta/v_bar + self.gamma*(dV*dlnJ)

    def predict_vij(self, u, d):
        return 1.0 / (1.0 + np.exp(-self.calculate_logit(u['V'], u['lnJ'], d['V'], d['lnJ'])))

def generate_v6_official_assignments():
    print("="*80)
    print("KSAU v6.0: Topological Freeze-out Algorithm")
    print("Status: Simulating Universe Cooling & Phase Transitions")
    print("="*80)
    
    phys = ksau_config.load_physical_constants()
    selector = FreezeOutSelector(phys)
    
    # 1. Load and Classify States
    df_l = pd.read_csv(ksau_config.load_linkinfo_path(), sep='|', skiprows=[1])
    df_k = pd.read_csv(ksau_config.load_knotinfo_path(), sep='|', skiprows=[1], low_memory=False)
    
    # Links setup
    for c in ['volume', 'crossing_number', 'components', 'determinant']:
        df_l[c] = pd.to_numeric(df_l[c], errors='coerce').fillna(0)
    
    # Knots setup (Always 1 component)
    for c in ['volume', 'crossing_number', 'determinant']:
        df_k[c] = pd.to_numeric(df_k[c], errors='coerce').fillna(0)
    df_k['components'] = 1

    # 2. Phase Separation: Torus (V=0) vs Hyperbolic (V>0)
    print("Separating Topological Phases...")
    torus_states = df_k[df_k['volume'] == 0].sort_values('crossing_number')
    hyper_states = df_k[df_k['volume'] > 0].sort_values('volume')
    hyper_links = df_l[df_l['volume'] > 0].sort_values('volume')

    # 3. Lepton Selection: The Boundary Crossover (Logic-based)
    # Rule: Electron is Torus (Gen 1), Muon/Tau are Hyperbolic (Gen 2/3)
    # We filter for non-trivial knots (Crossing N >= 3)
    print("\nPhase I: Lepton Freeze-out (Boundary Phase Transition)")
    assignments = {}
    
    # Electron: Simplest possible non-trivial Torus state (N >= 3)
    e_knot = torus_states[torus_states['crossing_number'] >= 3].iloc[0]
    
    # Muon: The first point of Hyperbolic crossover (Lowest volume V > 0)
    mu_knot = hyper_states.iloc[0]
    
    # Tau: Next generation ground state (Higher volume Hyperbolic)
    # Optimized for Ground State (low complexity N relative to V)
    tau_cands = hyper_states[hyper_states['volume'] > 3.0].head(10).copy()
    tau_cands['score'] = tau_cands['volume'] + 0.5 * tau_cands['crossing_number']
    tau_knot = tau_cands.sort_values('score').iloc[0]
    
    for i, (name, knot) in enumerate(zip(['Electron', 'Muon', 'Tau'], [e_knot, mu_knot, tau_knot])):
        assignments[name] = {"topology": knot['name'], "volume": float(knot['volume']), "crossing_number": int(knot['crossing_number']), "components": 1, "determinant": int(knot['determinant']), "generation": i + 1}
        print(f"  {name:<10} -> {knot['name']} (V={knot['volume']:.2f}, N={knot['crossing_number']})")

    # 4. Quark Selection: Ground State Search (Complexity-Volume balance)
    print("\nPhase II: Quark Freeze-out (Bulk Phase Resonance)")
    ckm_exp = np.array(phys['ckm']['matrix'])
    coeffs = ksau_config.get_kappa_coeffs()
    kappa = ksau_config.KAPPA
    
    quark_candidates = {}
    for q_name, q_meta in phys['quarks'].items():
        comp = 2 if q_name in ['Up', 'Charm', 'Top'] else 3
        twist = (2 - q_meta['generation']) * ((-1)**comp)
        target_v = (np.log(q_meta['observed_mass']) - kappa*twist - coeffs['quark_intercept']) / coeffs['quark_vol_coeff']
        
        subset = hyper_links[hyper_links['components'] == comp].copy()
        subset['vol_diff'] = (subset['volume'] - target_v).abs()
        
        # Rule: Prioritize Ground States (Lower crossing N for same volume)
        # Score = MAE_Volume + 0.1 * (Crossing / target_crossing)
        subset['score'] = subset['vol_diff'] + 0.05 * subset['crossing_number']
        
        cands = subset.sort_values('score').head(5)
        quark_candidates[q_name] = [{'name': r['name'], 'V': r['volume'], 'lnJ': np.log(max(1e-10, get_jones_mag(r['jones_polynomial']))), 'det': r['determinant'], 'crossing': r['crossing_number'], 'comp': r['components']} for _, r in cands.iterrows()]

    # Global Optimization over top candidates
    best_mae, best_set = float('inf'), None
    for c in quark_candidates['Charm'][:3]:
      for s in quark_candidates['Strange'][:3]:
        for b in quark_candidates['Bottom'][:3]:
          for t in quark_candidates['Top'][:3]:
            comb = {'Up': quark_candidates['Up'][0], 'Down': quark_candidates['Down'][0], 'Charm': c, 'Strange': s, 'Bottom': b, 'Top': t}
            mae = 0
            for i, u_n in enumerate(['Up', 'Charm', 'Top']):
                for j, d_n in enumerate(['Down', 'Strange', 'Bottom']):
                    mae += abs(selector.predict_vij(comb[u_n], comb[d_n]) - ckm_exp[i, j])
            if mae < best_mae: best_mae, best_set = mae, comb

    print(f"  Quark Selection Complete. Best Set MAE: {best_mae/9.0:.4e}")
    for q in best_set:
        assignments[q] = {"topology": best_set[q]['name'], "volume": best_set[q]['V'], "crossing_number": int(best_set[q]['crossing']), "components": int(best_set[q]['comp']), "determinant": int(best_set[q]['det']), "generation": phys['quarks'][q]['generation']}
        print(f"  {q:<10} -> {best_set[q]['name']} (N={best_set[q]['crossing']})")

    # 5. Bosons
    print("\nPhase III: Boson Localization...")
    for b_name in ['W', 'Z', 'Higgs']:
        target = 'L11a431' if b_name == 'Z' else ('L11n258' if b_name == 'W' else 'L11a427')
        match = df_l[df_l['name'].str.contains(target)].iloc[0]
        topo = f"{match['name']}{{0,0,0}}" if match['components']==3 else f"{match['name']}{{0,0}}"
        assignments[b_name] = {"topology": topo, "volume": float(match['volume']), "crossing_number": int(match['crossing_number']), "components": int(match['components']), "determinant": int(match['determinant']), "is_brunnian": (b_name != 'Higgs')}
        print(f"  {b_name:<10} -> {topo}")

    output_path = Path('v6.0/data/topology_assignments.json')
    with open(output_path, 'w') as f: json.dump(assignments, f, indent=2)
    print(f"\nSuccess: Freeze-out complete. Assignments saved to {output_path}")

if __name__ == "__main__":
    generate_v6_official_assignments()
