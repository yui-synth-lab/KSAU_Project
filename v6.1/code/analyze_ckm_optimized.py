import numpy as np
import pandas as pd
import utils_v61

def analyze_ckm_optimized():
    print("="*60)
    print("KSAU v6.1: Optimized CKM Scaling Law")
    print("="*60)

    # 1. Load Data
    _, links = utils_v61.load_data()
    
    # 2. Define Topologies
    quark_map = {
        "Up": "L8a6",
        "Down": "L6a4",
        "Strange": "L10n95",
        "Charm": "L11n64",
        "Bottom": "L10a140",
        "Top": "L11a62"
    }
    
    quarks = {}
    for q_name, topo_name in quark_map.items():
        row = links[links['name'] == topo_name]
        if row.empty:
             row = links[links['name'].str.startswith(topo_name + "{")]
        row = row.iloc[0]
        
        jones_val = utils_v61.get_jones_at_root_of_unity(row['jones_polynomial'], n=5)
        jones_mag = abs(jones_val)
        
        quarks[q_name] = {
            'V': float(row['volume']),
            'J': jones_mag,
            'topo': row['name']
        }

    # 3. Optimized Parameters (from optimize_ckm_coupling.py)
    # Model: ln|V| = A * dV + B * d(lnJ) + C
    A = -0.1193
    B = -3.0664
    C = 0.3232
    
    # 4. Experimental Data
    ckm_exp = {
        ('Up', 'Down'): 0.9743, ('Up', 'Strange'): 0.2253, ('Up', 'Bottom'): 0.0036,
        ('Charm', 'Down'): 0.2252, ('Charm', 'Strange'): 0.9734, ('Charm', 'Bottom'): 0.0410,
        ('Top', 'Down'): 0.0086, ('Top', 'Strange'): 0.0400, ('Top', 'Bottom'): 0.9991
    }

    print(f"Formula: |V_ij| = e^{C:.4f} * exp({A:.4f} * dV) * (J_min / J_max)^|{B:.4f}|")
    print(f"Interpretation: Mixing is suppressed by the cube of the topological complexity ratio.")
    print("-" * 60)
    print(f"{'Transition':<14} | {'dV':<6} | {'J_ratio':<8} | {'Pred':<8} | {'Obs':<8} | {'Error'}")
    print("-" * 60)

    predictions = []
    
    for (q1, q2), obs in ckm_exp.items():
        v1, j1 = quarks[q1]['V'], quarks[q1]['J']
        v2, j2 = quarks[q2]['V'], quarks[q2]['J']
        
        dV = abs(v1 - v2)
        dlnJ = abs(np.log(j1) - np.log(j2))
        
        # Calculate Prediction
        ln_pred = A * dV + B * dlnJ + C
        pred = np.exp(ln_pred)
        
        # Ratio for display
        j_ratio = min(j1, j2) / max(j1, j2)
        
        err = abs(obs - pred) / obs * 100
        
        print(f"{q1}-{q2:<7} | {dV:.2f}   | {j_ratio:.4f}   | {pred:.4f}   | {obs:.4f}   | {err:.1f}%")
        predictions.append(pred)

    # Calculate final R2
    obs_vals = np.array(list(ckm_exp.values()))
    pred_vals = np.array(predictions)
    
    # R2 on Log Scale (standard for CKM)
    log_obs = np.log(obs_vals)
    log_pred = np.log(pred_vals)
    ss_res = np.sum((log_obs - log_pred)**2)
    ss_tot = np.sum((log_obs - np.mean(log_obs))**2)
    r2 = 1 - (ss_res / ss_tot)
    
    print("-" * 60)
    print(f"Final R^2 (Log Scale): {r2:.6f}")
    print("-" * 60)
    
    # Physics Note
    print("\n[Physics Note]")
    print(f"The coefficient B = {B:.4f} suggests a scaling law:")
    print("  |V_ij| ~ (J_light / J_heavy)^3")
    print("This implies mixing is a third-order topological transition process.")

if __name__ == "__main__":
    analyze_ckm_optimized()
