"""
Detailed diagnosis: Why does LOO CV fail so badly?
Check if the issue is:
1. Fallback being triggered (quantum numbers filter fails)
2. Target values being too different
3. Selection strategy being too sensitive
"""

import pandas as pd
import numpy as np
import json
import ksau_config
from pathlib import Path
from topology_official_selector import select_physically_grounded_topology

def detailed_cv_diagnosis():
    """
    Run selection for each quark with detailed diagnostics.
    """
    print("="*80)
    print("DETAILED CROSS-VALIDATION DIAGNOSIS")
    print("="*80)
    
    phys = ksau_config.load_physical_constants()
    coeffs = ksau_config.get_kappa_coeffs()
    kappa = ksau_config.KAPPA
    
    # Load topology databases
    df_l = pd.read_csv(ksau_config.load_linkinfo_path(), sep='|', skiprows=[1])
    for c in ['volume', 'crossing_number', 'components', 'determinant']:
        df_l[c] = pd.to_numeric(df_l[c], errors='coerce').fillna(0)
    
    # Load current assignments
    assignments_path = Path(__file__).parent.parent / 'data' / 'topology_assignments.json'
    with open(assignments_path, 'r') as f:
        current = json.load(f)
    
    slope_q = coeffs['quark_vol_coeff']
    bq = coeffs['quark_intercept']
    
    print("\nQUARK SELECTION DIAGNOSTICS:")
    print("-" * 80)
    
    for q_name in ['Up', 'Down', 'Charm', 'Strange', 'Top', 'Bottom']:
        if q_name not in current:
            continue
        
        q_meta = phys['quarks'][q_name]
        observed_mass = q_meta['observed_mass']
        charge_type = q_meta['charge_type']
        gen = q_meta['generation']
        comp = 2 if charge_type == 'up-type' else 3
        
        # Calculate expected target volume
        twist = (2 - gen) * ((-1)**comp)
        target_v = (np.log(observed_mass) - kappa*twist - bq) / slope_q
        
        # Current assignment
        curr_assign = current[q_name]
        curr_topo = curr_assign['topology']
        curr_vol = curr_assign['volume']
        curr_det = curr_assign['determinant']
        
        print(f"\n{q_name}:")
        print(f"  Observed Mass: {observed_mass:.3f} MeV")
        print(f"  Calculated Target Volume: {target_v:.4f}")
        print(f"  Current Assignment: {curr_topo} (V={curr_vol:.4f}, Det={curr_det})")
        
        # Now try to re-select with the selection algorithm
        selected = select_physically_grounded_topology(df_l, target_v, 'quark', charge_type, 'volume', comp)
        
        if selected is None:
            print(f"  ❌ RE-SELECTION FAILED: No topology found!")
        else:
            new_topo = selected['name']
            new_vol = selected['volume']
            new_det = int(selected['determinant'])
            
            same = (new_topo == curr_topo.split('{')[0])  # Compare without parameters
            print(f"  RE-SELECTION: {new_topo} (V={new_vol:.4f}, Det={new_det})")
            print(f"  → Same topology? {same}")
            
            if not same:
                print(f"  ⚠️  DIFFERENT! This explains the CV failure.")
        
        # Check how many candidates pass the determinant filter
        mask = (df_l['components'] == comp) & (df_l['crossing_number'] <= 12)
        candidates = df_l[mask].copy()
        print(f"  Total candidates (comp={comp}): {len(candidates)}")
        
        # Apply quantum number filter
        from topology_official_selector import check_quantum_numbers
        candidates['phys_allowed'] = candidates.apply(
            lambda r: check_quantum_numbers(r, 'quark', charge_type), axis=1
        )
        allowed = candidates[candidates['phys_allowed']]
        print(f"  After Det filter: {len(allowed)}")
        
        if len(allowed) == 0:
            print(f"  ⚠️  NO CANDIDATES PASS FILTER - Fallback would be triggered!")
    
    print("\n" + "="*80)
    print("ROOT CAUSE ANALYSIS")
    print("="*80)
    print("""
The 0.78% MAE was computed on the SAME 12 particles used to design the algorithm.
When we hold out one particle and re-select topologies using the learned rules,
we get different results because:

1. **Determinant Rules are TOO STRICT**: Filters out better-matching topologies
   - Example: Up quark needs Det=4n (not 2^k), but maybe Det=16 (power of 2)
     was actually the best match and got filtered out.

2. **Fallback Logic Masks the Problem**: When no topology satisfies the rules,
   the code silently uses ANY topology, defeating the purpose of the rules.

3. **Target Volume Sensitivity**: The algorithm is sensitive to small changes
   in the target value, and without the constraint of "known" particles,
   the selection becomes unstable.

SOLUTION: Either:
  A) Make the Determinant rules less strict (more empirical, less theoretical)
  B) Remove the Determinant rules and optimize purely on energy matching
  C) Use a weighted ranking instead of hard filters
  D) Acknowledge this is an exploratory model and frame it differently in paper
""")

if __name__ == "__main__":
    detailed_cv_diagnosis()
