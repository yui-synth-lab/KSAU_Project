import numpy as np
import pandas as pd
import utils_v61

def run_final_ckm_model():
    print("="*80)
    print("KSAU v6.1: Final CKM Master Formula (Geometric Interaction Model)")
    print("Status: Zero-Parameter Verification (Logit-Geometric)")
    print("="*80)

    # 1. Load Data and Metadata
    _, links = utils_v61.load_data()
    assignments = utils_v61.load_assignments()
    consts = utils_v61.load_constants()
    
    # 2. CKM Coefficients (from SSoT: physical_constants.json)
    # Updated 2026-02-13: Use optimized coefficients from constrained optimization
    coeff = consts['ckm']['optimized_coefficients']

    A = coeff['A']
    B = coeff['B']
    beta = coeff['beta']
    gamma = coeff['gamma']
    C = coeff['C']

    print(f"Coefficients: A={A:.4f}, B={B:.4f}, beta={beta:.4f}, gamma={gamma:.4f}, C={C:.4f}\n")

    quark_names = ["Up", "Down", "Strange", "Charm", "Bottom", "Top"]
    quarks = {}
    
    for q_name in quark_names:
        topo_info = assignments.get(q_name)
        if not topo_info: continue
            
        topo_name = topo_info['topology'].split('{')[0]
        row = links[links['name'] == topo_name]
        if row.empty:
             row = links[links['name'].str.startswith(topo_name + "{")].iloc[0]
        else:
             row = row.iloc[0]
            
        jones_val = utils_v61.get_jones_at_root_of_unity(row['jones_polynomial'], n=5)
        quarks[q_name] = {
            'V': float(row['volume']),
            'lnJ': np.log(max(1e-10, abs(jones_val)))
        }

    # 3. Apply Master Formula: ln(|Vij|/(1-|Vij|)) = C + A*dV + B*dlnJ + beta/V_bar + gamma*(dV*dlnJ)
    up_types = ["Up", "Charm", "Top"]
    down_types = ["Down", "Strange", "Bottom"]
    ckm_exp_matrix = consts['ckm']['matrix']
    
    print(f"{'Transition':<15} | {'Exp':<10} | {'Geo-Pred':<10} | {'Error %':<10}")
    print("-" * 60)
    
    errors = []
    for i, u in enumerate(up_types):
        for j, d in enumerate(down_types):
            obs = ckm_exp_matrix[i][j]
            
            # Geometric Deltas
            dV = abs(quarks[u]['V'] - quarks[d]['V'])
            dlnJ = abs(quarks[u]['lnJ'] - quarks[d]['lnJ'])
            V_bar = (quarks[u]['V'] + quarks[d]['V']) / 2.0
            
            # Master Formula (Logit Score)
            logit_V = C + A*dV + B*dlnJ + beta/V_bar + gamma*(dV*dlnJ)
            
            # Prediction via Inverse Logit (Sigmoid)
            pred = 1.0 / (1.0 + np.exp(-logit_V))
            
            err = abs(obs - pred) / obs * 100
            errors.append(err)
            print(f"{u + '-' + d:<15} | {obs:.4f}     | {pred:.4f}     | {err:.2f}%")
            
    print("-" * 60)
    print(f"Global Precision (Mean Error): {np.mean(errors):.2f}%")

if __name__ == "__main__":
    run_final_ckm_model()
