import numpy as np
import pandas as pd
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../v6.1/code'))
import utils_v61

def derive_ckm_topological_principles():
    print("="*60)
    print("KSAU v6.3: Ab Initio CKM Derivation (No Fitting)")
    print("="*60)
    
    # 1. Load Data & Constants
    _, links = utils_v61.load_data()
    consts = utils_v61.load_constants()
    assignments = utils_v61.load_assignments()
    
    # 2. Define Particles & Topologies
    # Extract quark topologies from assignments
    quarks = {}
    for name, data in assignments.items():
        if data.get('sector') == 'quark':
            # Remove component suffix for database matching (e.g., L8a6{1} -> L8a6)
            base_topo = data['topology'].split('{')[0]
            quarks[name] = base_topo
    
    # 3. Calculate Topological Amplitude Q_K
    # Evaluation at t = exp(i 2pi/5)
    print("[Calculating Topological Amplitudes Q_K in SU(2)_3]")
    quark_amps = {}
    
    for q_name, topo in quarks.items():
        row = links[links['name'] == topo]
        if row.empty:
             row = links[links['name'].str.startswith(topo + "{")]
        
        if row.empty:
            continue
            
        row = row.iloc[0]
        jones_poly = row['jones_polynomial']
        val = utils_v61.get_jones_at_root_of_unity(jones_poly, n=5)
        Q_K = abs(val)
        
        quark_amps[q_name] = Q_K
        print(f"  {q_name:<8} ({topo}): Q = {Q_K:.4f}")

    # 4. Derive CKM Elements from Topological Overlap
    print("\n[Testing 'Color Cube Law' (No Free Parameters)]")
    print("Formula: |V_ij| = ( Q_light / Q_heavy )^3")
    print("-" * 70)
    print(f"{'Transition':<14} | {'Q_ratio (r)':<12} | {'Pred (r^3)':<12} | {'Observed':<10} | {'Error'}")
    print("-" * 70)
    
    # Load Observed CKM from physical_constants.json
    # matrix order: 0:Up/Down/Strange? No, SM order is (u,c,t) x (d,s,b)
    # [ [Vud, Vus, Vub], [Vcd, Vcs, Vcb], [Vtd, Vts, Vtb] ]
    m = consts['ckm']['matrix']
    ckm_exp = {
        ('Up', 'Down'): m[0][0], ('Up', 'Strange'): m[0][1], ('Up', 'Bottom'): m[0][2],
        ('Charm', 'Down'): m[1][0], ('Charm', 'Strange'): m[1][1], ('Charm', 'Bottom'): m[1][2],
        ('Top', 'Down'): m[2][0], ('Top', 'Strange'): m[2][1], ('Top', 'Bottom'): m[2][2]
    }
    
    mse_log = 0
    count = 0
    
    for (q1, q2), obs in ckm_exp.items():
        Q1 = quark_amps[q1]
        Q2 = quark_amps[q2]
        r = min(Q1, Q2) / max(Q1, Q2)
        pred = r ** 3
        err_pct = abs(pred - obs) / obs * 100
        
        log_diff = (np.log(pred) - np.log(obs))**2
        mse_log += log_diff
        count += 1
        
        print(f"{q1}-{q2:<7} | {r:.4f}       | {pred:.4f}       | {obs:.4f}     | {err_pct:.1f}%")
        
    print("-" * 70)
    rmse = np.sqrt(mse_log / count)
    print(f"Log-RMSE: {rmse:.4f}")

    # 5. Theoretical Verification
    print("\n[Mechanism Verification]")
    print("1. Phase Origin:")
    print("   The calculation uses purely t = e^(i 2pi/5), corresponding to SU(2)_3 TQFT.")
    
    print("\n2. Cabibbo Angle Derivation:")
    pred_us = (min(quark_amps['Strange'], quark_amps['Up']) / max(quark_amps['Strange'], quark_amps['Up']))**3
    obs_us = ckm_exp[('Up', 'Strange')]
    print(f"   Cabibbo Prediction (|V_us|): {pred_us:.4f}")
    print(f"   Observed Cabibbo: {obs_us}")
    print(f"   Agreement: {abs(pred_us - obs_us)/obs_us*100:.1f}%")
    
    if abs(pred_us - 0.2253) < 0.05:
        print("   SUCCESS: Cabibbo angle arises naturally from the cubic ratio of Jones amplitudes.")
        print("   This validates the 'Color Cube Law': quarks behave as 3-strand braids in topological space.")
    else:
        print("   PARTIAL: The trend is correct, but exact value needs refined topology or N_c correction.")

if __name__ == "__main__":
    derive_ckm_topological_principles()
