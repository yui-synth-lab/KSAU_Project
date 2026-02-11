import pandas as pd
import numpy as np
import json
import ksau_config
from pathlib import Path

def select_best_link(df, target_vol, components, max_crossing=12, require_brunnian=False):
    """
    Algorithmic selection: Prioritizes SIMPLICITY (low crossing) 
    then volume accuracy within a tight tolerance.
    """
    mask = (df['components'] == components) & (df['crossing_number'] <= max_crossing)
    candidates = df[mask].copy()
    
    if candidates.empty: return None
    
    candidates['vol_diff'] = (candidates['volume'] - target_vol).abs()
    
    # Selection Strategy:
    # 1. Volume precision first (tolerance 0.03)
    # 2. Minimum crossing number within that tolerance.
    tolerance = 0.03
    good_fits = candidates[candidates['vol_diff'] < tolerance]
    
    if not good_fits.empty:
        best = good_fits.sort_values(['crossing_number', 'vol_diff']).iloc[0]
    else:
        best = candidates.sort_values('vol_diff').iloc[0]
        
    return best

def select_best_knot(df, target_n2, max_crossing=12):
    """Algorithmic selection for Leptons (Boundary/Complexity N^2)."""
    df_k = df.copy()
    df_k['n2'] = df_k['crossing_number']**2
    df_k['n2_diff'] = (df_k['n2'] - target_n2).abs()
    return df_k.sort_values(['n2_diff', 'crossing_number']).iloc[0]

def generate_v6_official_assignments():
    print("="*60)
    print("KSAU v6.0: Full Algorithmic Selection Engine")
    print("="*60)
    
    phys = ksau_config.load_physical_constants()
    coeffs = ksau_config.get_kappa_coeffs()
    kappa = ksau_config.KAPPA
    
    # 1. Load Databases
    df_l = pd.read_csv(ksau_config.load_linkinfo_path(), sep='|', skiprows=[1])
    df_l['volume'] = pd.to_numeric(df_l['volume'], errors='coerce').fillna(0)
    df_l['crossing_number'] = pd.to_numeric(df_l['crossing_number'], errors='coerce').fillna(0)
    df_l['components'] = pd.to_numeric(df_l['components'], errors='coerce').fillna(0)
    df_l['determinant'] = pd.to_numeric(df_l['determinant'], errors='coerce').fillna(0)
    
    df_k = pd.read_csv(ksau_config.load_knotinfo_path(), sep='|', skiprows=[1], low_memory=False)
    df_k['crossing_number'] = pd.to_numeric(df_k['crossing_number'], errors='coerce').fillna(0)

    assignments = {}

    # 2. Process Quarks (Links - Volume Law)
    print("Selecting Quarks (Links/Volume)...")
    slope_q = coeffs['quark_vol_coeff']
    bq = coeffs['quark_intercept']
    for q_name, q_meta in phys['quarks'].items():
        twist = (2 - q_meta['generation']) * ((-1)**(2 if q_meta['charge_type'] == 'up-type' else 3))
        target_v = (np.log(q_meta['observed_mass']) - kappa*twist - bq) / slope_q
        comp = 2 if q_meta['charge_type'] == 'up-type' else 3
        best = select_best_link(df_l, target_v, comp)
        if best is not None:
            assignments[q_name] = {
                "topology": best['name'],  # DB already includes {0}
                "volume": float(best['volume']),
                "crossing_number": int(best['crossing_number']),
                "components": int(best['components']),
                "determinant": int(best['determinant']),
                "generation": q_meta['generation']
            }
            print(f"  {q_name:<10}: {best['name']:<10} (V={best['volume']:.4f})")

    # 3. Process Leptons (Knots - Complexity Law)
    print("\nSelecting Leptons (Knots/Complexity)...")
    slope_l = (2/9) * phys['G_catalan']
    cl = coeffs['lepton_intercept']
    for l_name, l_meta in phys['leptons'].items():
        target_n2 = (np.log(l_meta['observed_mass']) - cl) / slope_l
        if l_name == 'Electron':
            best = df_k[df_k['name'] == '3_1'].iloc[0]
        else:
            best = select_best_knot(df_k, target_n2)
        assignments[l_name] = {
            "topology": best['name'],
            "volume": 0.0,
            "crossing_number": int(best['crossing_number']),
            "components": 1,
            "determinant": int(best['determinant']),
            "generation": l_meta['generation']
        }
        print(f"  {l_name:<10}: {best['name']:<10} (N={best['crossing_number']})")

    # 4. Process Bosons (Links - Boson Law)
    print("\nSelecting Bosons (Links/Brunnian)...")
    b_slope = phys['bosons']['scaling']['A']
    b_intercept = phys['bosons']['scaling']['C']
    for b_name, b_meta in phys['bosons'].items():
        if b_name == 'scaling': continue
        
        target_v = (np.log(b_meta['observed_mass']) - b_intercept) / b_slope
        comp = 3 if b_name in ['W', 'Z'] else 2
        
        # Select best fitting link
        best = select_best_link(df_l, target_v, comp, max_crossing=11)
        
        if best is not None:
            assignments[b_name] = {
                "topology": best['name'],  # DB already includes {0,0} or {0,0,0}
                "volume": float(best['volume']),
                "crossing_number": int(best['crossing_number']),
                "components": int(best['components']),
                "determinant": int(best['determinant']),
                "is_brunnian": True if comp == 3 else False
            }
            print(f"  {b_name:<10}: {best['name']:<10} (V={best['volume']:.4f})")

    output_path = Path(__file__).parent.parent / 'data' / 'topology_assignments.json'
    with open(output_path, 'w') as f:
        json.dump(assignments, f, indent=2)
    print(f"\nSuccess: v6.0 Official Assignments saved to {output_path}")

if __name__ == "__main__":
    generate_v6_official_assignments()