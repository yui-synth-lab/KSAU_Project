
import sys
import numpy as np
import pandas as pd
from pathlib import Path
import json
from scipy.stats import linregress

# AIRDP SSoT Loader setup
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
ssot_path = project_root / "ssot"
sys.path.insert(0, str(ssot_path))    
from ksau_ssot import SSOT

def main():
    ssot = SSOT()
    consts = ssot.constants()
    topo_assignments = ssot.topology_assignments()
    knots_df, links_df = ssot.knot_data()
    
    # 1. Collect Particle Data
    lifetimes = {
        "Muon": 2.1969811e-6,
        "Tau": 290.3e-15,
        "Top": 4.67e-25,
        "W": 3.16e-25,
        "Z": 2.64e-25,
        "Higgs": 1.62e-22,
        "Charm": 1.041e-12 / 658.2, # Width to Lifetime proxy if needed, but use SSoT widths
    }
    
    data = []
    particle_groups = [
        ('quark', consts['particle_data']['quarks']),
        ('lepton', consts['particle_data']['leptons']),
        ('boson', consts['particle_data']['bosons'])
    ]
    
    for p_type, group in particle_groups:
        for name, p_data in group.items():
            if 'observed_decay_width_mev' not in p_data:
                continue
                
            width = p_data['observed_decay_width_mev']
            topo_info = topo_assignments[name]
            topo_name = topo_info['topology']
            n = topo_info['crossing_number']
            det = topo_info['determinant']
            
            u = 0
            s = 0
            if topo_info['components'] == 1:
                row = knots_df[knots_df['name'] == topo_name]
                if not row.empty:
                    u = float(row['unknotting_number'].iloc[0]) if pd.notna(row['unknotting_number'].iloc[0]) else 0
                    s = float(row['signature'].iloc[0]) if pd.notna(row['signature'].iloc[0]) else 0
            else:
                row = links_df[links_df['name'] == topo_name]
                if not row.empty:
                    u = float(row['unlinking_number'].iloc[0]) if pd.notna(row['unlinking_number'].iloc[0]) else 0
                    if pd.isna(u): u = float(row['splitting_number'].iloc[0]) if pd.notna(row['splitting_number'].iloc[0]) else 0
                    s = float(row['signature'].iloc[0]) if pd.notna(row['signature'].iloc[0]) else 0
            
            data.append({
                "name": name, "type": p_type, "width": width,
                "n": n, "det": det, "u": u, "s": s
            })
            
    df = pd.DataFrame(data)
    df['ln_width'] = np.log(df['width'])
    
    # 2. Refined TSI Formulation
    # Logic: Gamma ~ 1/TSI. ln(Gamma) ~ -ln(TSI)
    # Signs from SSoT model: n(+), |s|(-), ln(Det)(+), u(-) for ln(Gamma)
    # So TSI should have: |s|(+) , u(+) in numerator; n(+) , ln(Det)(+) in denominator.
    
    # TSI_ref = (|s| + delta) * (u + 1) / (n * ln(Det))
    
    deltas = [0.1, 0.5, 1.0, 2.0]
    results_summary = []
    
    print("--- Refined TSI (Sign-Consistent) Search ---")
    for delta in deltas:
        df[f'TSI_d{delta}'] = (np.abs(df['s']) + delta) * (df['u'] + 1) / (df['n'] * np.log(df['det']))
        # We expect negative correlation between ln(TSI) and ln(width)
        slope, intercept, r_value, p_value, std_err = linregress(np.log(df[f'TSI_d{delta}']), df['ln_width'])
        r2 = r_value**2
        print(f"delta={delta}: R2 = {r2:.4f}, p = {p_value:.4e}, slope = {slope:.2f}")
        results_summary.append({"delta": delta, "r2": r2, "p_value": p_value})

    # 3. Handle s=0 specifically for W and Muon/Tau
    # W has s=0, Muon/Tau have s=0. 
    # But W is unstable, Muon/Tau are stable.
    # The current TSI_ref gives them the SAME (s+delta) factor.
    # What's the difference? Muon/Tau are knots (C=1), W is a link (C=3).
    # Link component count C should probably be in the denominator of TSI (reducing stability).
    
    df['comp'] = df['name'].map(lambda x: topo_assignments[x]['components'])
    
    print("\n--- Testing Component-Corrected TSI ---")
    # TSI_comp = (|s| + 1) * (u + 1) / (n * ln(Det) * sqrt(comp))
    df['TSI_comp'] = (np.abs(df['s']) + 1.0) * (df['u'] + 1) / (df['n'] * np.log(df['det']) * np.sqrt(df['comp']))
    slope, intercept, r_value, p_value, std_err = linregress(np.log(df['TSI_comp']), df['ln_width'])
    print(f"TSI_comp: R2 = {r_value**2:.4f}, p = {p_value:.4e}")

    # 4. Save best
    results = {
        "iteration": 5,
        "hypothesis_id": "H43",
        "timestamp": "2026-02-26T19:30:00Z",
        "task_name": "TSI Refinement for Decay Widths",
        "best_r2": float(r_value**2),
        "data": df.to_dict(orient='records')
    }
    
    output_dir = project_root / "cycles" / "cycle_17" / "iterations" / "iter_05"
    with open(output_dir / "results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
