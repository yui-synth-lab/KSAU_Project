import pandas as pd
import numpy as np
import json
import ksau_config
from pathlib import Path
from sklearn.linear_model import LinearRegression
import re

# ============================================================================
# UTILITIES
# ============================================================================

def parse_polynomial(poly_str, val):
    if pd.isna(poly_str): return 0.0
    poly_str = str(poly_str).replace(' ', '').replace('t', 'x').replace('q', 'x')
    expr = poly_str.replace('^', '**')
    x = val
    try:
        clean_expr = re.sub(r'x[0-9]+', 'x', expr)
        return eval(clean_expr)
    except:
        return 0.0

def get_jones_mag(poly_str):
    phase = np.exp(1j * 2 * np.pi / 5)
    val = parse_polynomial(poly_str, phase)
    return abs(val)

# ============================================================================
# PHYSICAL CONSTRAINTS
# ============================================================================

def is_power_of_two(n):
    return n > 0 and (n & (n - 1)) == 0

def is_physically_allowed(row, charge_type):
    det = int(row['determinant'])
    if charge_type == 'down-type':
        return is_power_of_two(det)
    elif charge_type == 'up-type':
        return (det % 4 == 0) and not is_power_of_two(det)
    return True

# ============================================================================
# OPTIMIZATION ENGINE
# ============================================================================

def get_candidates(df, target_vol, charge_type, comp, top_n=5):
    mask = (df['components'] == comp) & (df['crossing_number'] <= 12)
    candidates = df[mask].copy()
    candidates['allowed'] = candidates.apply(lambda r: is_physically_allowed(r, charge_type), axis=1)
    allowed = candidates[candidates['allowed']].copy()
    if allowed.empty: return pd.DataFrame()
    allowed['vol_diff'] = (allowed['volume'] - target_vol).abs()
    return allowed.sort_values('vol_diff').head(top_n)

def calculate_ckm_score_v2(combination, ckm_exp_log):
    """
    Evaluates a combination using Fixed A=-0.5, B*dlnJ, and Tunneling beta/Vbar.
    """
    up_types = ['Up', 'Charm', 'Top']
    down_types = ['Down', 'Strange', 'Bottom']
    
    X = []
    y = []
    
    for i, u in enumerate(up_types):
        for j, d in enumerate(down_types):
            dV = abs(combination[u]['V'] - combination[d]['V'])
            dlnJ = abs(combination[u]['lnJ'] - combination[d]['lnJ'])
            v_bar = (combination[u]['V'] + combination[d]['V']) / 2.0
            
            # Target for B*dlnJ + beta/V_bar + C
            target = ckm_exp_log[i][j] + 0.5 * dV
            X.append([dlnJ, 1.0 / v_bar])
            y.append(target)
            
    X = np.array(X)
    y = np.array(y)
    reg = LinearRegression().fit(X, y)
    r2_residual = reg.score(X, y)
    
    # Calculate global R2
    preds_log = -0.5 * np.array([abs(combination[u]['V'] - combination[d]['V']) for u in up_types for d in down_types]) + reg.predict(X)
    y_true = ckm_exp_log.flatten()
    ss_res = np.sum((y_true - preds_log)**2)
    ss_tot = np.sum((y_true - np.mean(y_true))**2)
    r2_global = 1 - (ss_res / ss_tot)
    
    return r2_global, reg.coef_

def generate_v6_official_assignments():
    print("="*80)
    print("KSAU v6.0: Unified Global Flavor Fit (Tunneling Enabled)")
    print("Logic: Fixed A=-0.5, Entropy Suppression, Mass-Dependent Tunneling")
    print("="*80)
    
    phys = ksau_config.load_physical_constants()
    coeffs = ksau_config.get_kappa_coeffs()
    kappa = ksau_config.KAPPA
    
    df_l = pd.read_csv(ksau_config.load_linkinfo_path(), sep='|', skiprows=[1])
    for c in ['volume', 'crossing_number', 'components', 'determinant']:
        df_l[c] = pd.to_numeric(df_l[c], errors='coerce').fillna(0)
    
    df_k = pd.read_csv(ksau_config.load_knotinfo_path(), sep='|', skiprows=[1], low_memory=False)
    df_k['crossing_number'] = pd.to_numeric(df_k['crossing_number'], errors='coerce').fillna(0)
    df_k['determinant'] = pd.to_numeric(df_k['determinant'], errors='coerce').fillna(0)

    ckm_exp = np.array(phys['ckm']['matrix'])
    ckm_exp_log = np.log(ckm_exp)

    # 1. Quarks: Global Search
    slope_q = coeffs['quark_vol_coeff']
    bq = coeffs['quark_intercept']
    
    quark_candidates = {}
    for q_name, q_meta in phys['quarks'].items():
        comp = 2 if q_meta['charge_type'] == 'up-type' else 3
        twist = (2 - q_meta['generation']) * ((-1)**comp)
        target_v = (np.log(q_meta['observed_mass']) - kappa*twist - bq) / slope_q
        cands = get_candidates(df_l, target_v, q_meta['charge_type'], comp, top_n=5)
        
        cand_list = []
        for _, row in cands.iterrows():
            j_val = get_jones_mag(row['jones_polynomial'])
            cand_list.append({
                'name': row['name'],
                'V': float(row['volume']),
                'J': j_val,
                'lnJ': np.log(j_val) if j_val > 0 else 0,
                'det': int(row['determinant']),
                'crossing': int(row['crossing_number']),
                'components': int(row['components'])
            })
        quark_candidates[q_name] = cand_list

    best_overall_score = -1
    best_set = None
    
    # Increase search space slightly for Top
    u_cands = quark_candidates['Up']
    d_cands = quark_candidates['Down']
    c_cands = quark_candidates['Charm']
    s_cands = quark_candidates['Strange']
    b_cands = quark_candidates['Bottom']
    t_cands = quark_candidates['Top']

    print("  Optimizing global fit...")
    for u in u_cands[0:1]: # Fix Up/Down for stability
      for d in d_cands[0:1]:
        for c in c_cands:
          for s in s_cands:
            for b in b_cands:
              for t in t_cands:
                combination = {'Up': u, 'Charm': c, 'Top': t, 'Down': d, 'Strange': s, 'Bottom': b}
                r2, coeffs_reg = calculate_ckm_score_v2(combination, ckm_exp_log)
                if r2 > best_overall_score:
                    best_overall_score = r2
                    best_set = combination
                    best_coeffs = coeffs_reg

    print(f"  Best Global R^2: {best_overall_score:.4f}")
    
    assignments = {}
    for q_name in ['Up', 'Down', 'Strange', 'Charm', 'Bottom', 'Top']:
        sel = best_set[q_name]
        assignments[q_name] = {
            "topology": f"{sel['name']}{{0}}",
            "volume": sel['V'],
            "crossing_number": sel['crossing'],
            "components": sel['components'],
            "determinant": sel['det'],
            "generation": phys['quarks'][q_name]['generation']
        }
        print(f"  {q_name:<8}: {sel['name']:<10} (Det={sel['det']}, V={sel['V']:.4f})")

    # 2. Leptons
    print("\nPhase 2: Selecting Leptons...")
    slope_l = (2/9) * phys['G_catalan']
    cl = -2.38
    for l_name, l_meta in phys['leptons'].items():
        if l_name == 'Electron':
            best = df_k[df_k['name'] == '3_1'].iloc[0]
        else:
            target_log_m = np.log(l_meta['observed_mass'])
            gen = l_meta['generation']
            twist = gen - 2
            target_n2 = (target_log_m - cl - kappa*twist + kappa*np.log(5)) / slope_l
            target_n = np.sqrt(max(0, target_n2))
            df_k['n_diff'] = (df_k['crossing_number'] - target_n).abs()
            best = df_k.sort_values('n_diff').iloc[0]
        assignments[l_name] = {
            "topology": best['name'],
            "volume": 0.0,
            "crossing_number": int(best['crossing_number']),
            "components": 1,
            "determinant": int(best['determinant']),
            "generation": l_meta['generation']
        }
        print(f"  {l_name:<8}: {best['name']:<10} (N={best['crossing_number']})")

    # 3. Bosons
    print("\nPhase 3: Bosons...")
    OFFICIAL_BOSONS = {'W': 'L11n387', 'Z': 'L11a431', 'Higgs': 'L11a55'}
    for b_name, base_topo in OFFICIAL_BOSONS.items():
        row = df_l[df_l['name'].str.startswith(base_topo)].iloc[0]
        assignments[b_name] = {
            "topology": f"{base_topo}{{0,0,0}}" if b_name != 'Higgs' else f"{base_topo}{{0,0}}",
            "volume": float(row['volume']),
            "crossing_number": int(row['crossing_number']),
            "components": int(row['components']),
            "determinant": int(row['determinant']),
            "is_brunnian": True if b_name in ['W', 'Z'] else False
        }
        print(f"  {b_name:<8}: {base_topo}")

    output_path = Path(__file__).parent.parent / 'data' / 'topology_assignments.json'
    with open(output_path, 'w') as f:
        json.dump(assignments, f, indent=2)
    print(f"\nSuccess: Assignments updated to v6.0 Standard at {output_path}")

if __name__ == "__main__":
    generate_v6_official_assignments()
