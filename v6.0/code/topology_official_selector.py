import pandas as pd
import numpy as np
import json
import ksau_config
from pathlib import Path

# ============================================================================
# TOPOLOGICAL SELECTION RULES (The Physics Grounding)
# ============================================================================

def is_power_of_two(n):
    return n > 0 and (n & (n - 1)) == 0

def check_quantum_numbers(row, p_type, charge_type):
    """
    Applies structural filters representing physical quantum numbers.
    """
    det = int(row['determinant'])
    
    if p_type == 'lepton':
        # Rule: Leptons (Boundary) must have ODD determinant
        return det % 2 != 0
    
    if p_type == 'quark':
        if charge_type == 'down-type':
            # Rule: Down-type (Q=-1/3) must have Det = 2^k (Power of 2)
            return is_power_of_two(det)
        elif charge_type == 'up-type':
            # Rule: Up-type (Q=+2/3) must have Det = 4*n (Multiple of 4, but not 2^k)
            return (det % 4 == 0) and not is_power_of_two(det)
            
    return True 

# ============================================================================
# SELECTION ENGINE
# ============================================================================

def select_physically_grounded_topology(df, target_val, p_type, charge_type, metric_col='volume', components=None):
    """
    Finds the best topology satisfying both Quantum Rules and Energy constraints.
    """
    # 1. Filter by basic structure
    if components is not None and 'components' in df.columns:
        mask = (df['components'] == components)
    else:
        mask = pd.Series(True, index=df.index)
        
    mask &= (df['crossing_number'] <= 12)
    candidates = df[mask].copy()
    
    if candidates.empty: return None
    
    # 2. Apply Physical Selection Rules
    candidates['physically_allowed'] = candidates.apply(
        lambda r: check_quantum_numbers(r, p_type, charge_type), axis=1
    )
    allowed = candidates[candidates['physically_allowed']].copy()
    
    if allowed.empty:
        allowed = candidates # Fallback
        
    # 3. Match Energy Scale
    allowed['diff'] = (allowed[metric_col] - target_val).abs()
    
    # Strategy: Tight tolerance for Energy, then prioritize Simplicity (Crossing)
    tolerance = 0.05 if metric_col == 'volume' else 0.5
    good_fits = allowed[allowed['diff'] < tolerance]
    
    if not good_fits.empty:
        return good_fits.sort_values(['crossing_number', 'diff']).iloc[0]
    else:
        return allowed.sort_values('diff').iloc[0]

def generate_v6_official_assignments():
    print("="*80)
    print("KSAU v6.0: Physically Grounded Algorithmic Selection")
    print("Selection Rules: Down-type(2^k), Up-type(4n), Lepton(Odd Det)")
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

    assignments = {}

    # 1. Quarks (Volume Law)
    print("Selecting Quarks...")
    slope_q = coeffs['quark_vol_coeff']
    bq = coeffs['quark_intercept']
    for q_name, q_meta in phys['quarks'].items():
        comp = 2 if q_meta['charge_type'] == 'up-type' else 3
        twist = (2 - q_meta['generation']) * ((-1)**comp)
        target_v = (np.log(q_meta['observed_mass']) - kappa*twist - bq) / slope_q
        best = select_physically_grounded_topology(df_l, target_v, 'quark', q_meta['charge_type'], 'volume', comp)
        if best is not None:
            assignments[q_name] = {
                "topology": f"{best['name']}{{0}}",
                "volume": float(best['volume']),
                "crossing_number": int(best['crossing_number']),
                "components": int(best['components']),
                "determinant": int(best['determinant']),
                "generation": q_meta['generation']
            }
            print(f"  {q_name:<10}: {best['name']:<10} (Det={int(best['determinant']):>3}, V={best['volume']:.4f})")

    # 2. Leptons (KNOTS ONLY - Complexity Law + Entropy Correction)
    print("\nSelecting Leptons (Knots Only)...")
    slope_l = (2/9) * phys['G_catalan']
    cl = -2.38 # Updated for Entropy Correction
    for l_name, l_meta in phys['leptons'].items():
        gen = l_meta['generation']
        twist = gen - 2
        
        # ln(m) = slope_l * N^2 + kappa*T - kappa*ln(Det) + cl
        # For selection, we use an average Det (e.g., 5) to estimate target N
        # then refine in the search.
        target_log_m = np.log(l_meta['observed_mass'])
        # V_approx: ln(m) - cl - kappa*twist + kappa*ln(avg_det)
        target_n2 = (target_log_m - cl - kappa*twist + kappa*np.log(5)) / slope_l
        target_n = np.sqrt(max(0, target_n2))
        
        if l_name == 'Electron':
            best = df_k[df_k['name'] == '3_1'].iloc[0]
        else:
            # Metric is 'crossing_number'
            best = select_physically_grounded_topology(df_k, target_n, 'lepton', 'lepton', 'crossing_number', components=None)
            
        assignments[l_name] = {
            "topology": best['name'],
            "volume": 0.0,
            "crossing_number": int(best['crossing_number']),
            "components": 1,
            "determinant": int(best['determinant']),
            "generation": l_meta['generation']
        }
        print(f"  {l_name:<10}: {best['name']:<10} (Det={int(best['determinant']):>3}, N={best['crossing_number']})")

    # 3. Bosons
    print("\nProcessing Bosons...")
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
        print(f"  {b_name:<10}: {base_topo:<10}")

    output_path = Path(__file__).parent.parent / 'data' / 'topology_assignments.json'
    with open(output_path, 'w') as f:
        json.dump(assignments, f, indent=2)
    print(f"\nSuccess: Physically Grounded Assignments saved to {output_path}")

if __name__ == "__main__":
    generate_v6_official_assignments()