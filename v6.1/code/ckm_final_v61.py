import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import utils_v61

def run_final_ckm_model():
    print("="*60)
    print("KSAU v6.1: Final CKM Model (Log-Interference)")
    print("="*60)

    # 1. Load Data and Metadata
    _, links = utils_v61.load_data()
    assignments = utils_v61.load_assignments()
    consts = utils_v61.load_constants()
    
    # 2. Extract Topologies from Central Metadata
    quark_names = ["Up", "Down", "Strange", "Charm", "Bottom", "Top"]
    quarks = {}
    
    for q_name in quark_names:
        topo_info = assignments.get(q_name)
        if not topo_info:
            continue
            
        topo_name = topo_info['topology'].split('{')[0] # Get base name
        row = links[links['name'] == topo_name]
        if row.empty:
             row = links[links['name'].str.startswith(topo_name + "{")]
        
        if row.empty:
            print(f"Warning: Topology {topo_name} not found in LinkInfo for {q_name}")
            continue
            
        row = row.iloc[0]
        jones_val = utils_v61.get_jones_at_root_of_unity(row['jones_polynomial'], n=5)
        quarks[q_name] = {
            'V': float(row['volume']),
            'J': abs(jones_val),
            'ln_J': np.log(abs(jones_val))
        }

    # 3. Experimental Data from Central Constants
    ckm_matrix = consts['ckm']['matrix']
    # Map matrix indices to (up-type, down-type) pairs
    # Rows: Up (0), Charm (1), Top (2)
    # Cols: Down (0), Strange (1), Bottom (2)
    up_types = ["Up", "Charm", "Top"]
    down_types = ["Down", "Strange", "Bottom"]
    
    ckm_exp = {}
    for i, u in enumerate(up_types):
        for j, d in enumerate(down_types):
            ckm_exp[(u, d)] = ckm_matrix[i][j]

    # 4. Final Regression: ln|Vij| = A * dV + B * d(lnJ) + C
    X = []
    y = []
    labels = []
    
    for (q1, q2), val in ckm_exp.items():
        dV = abs(quarks[q1]['V'] - quarks[q2]['V'])
        dlnJ = abs(quarks[q1]['ln_J'] - quarks[q2]['ln_J'])
        X.append([dV, dlnJ])
        y.append(np.log(val))
        labels.append(f"{q1}-{q2}")
        
    X = np.array(X)
    y = np.array(y)
    
    reg = LinearRegression()
    reg.fit(X, y)
    r2 = reg.score(X, y)
    preds_log = reg.predict(X)
    
    print(f"Model: ln|Vij| = A * dV + B * ln(J_ratio) + C")
    print(f"A (Vol Coeff): {reg.coef_[0]:.4f}")
    print(f"B (Topo Coeff): {reg.coef_[1]:.4f} (Expect ~ -3)")
    print(f"C (Intercept): {reg.intercept_:.4f}")
    print(f"R^2: {r2:.4f}")
    
    print("\nPredictions:")
    print(f"{'Pair':<12} | {'Obs':<8} | {'Pred':<8} | {'Error %':<8}")
    for i, label in enumerate(labels):
        obs = np.exp(y[i])
        pred = np.exp(preds_log[i])
        err = abs(obs - pred) / obs * 100
        print(f"{label:<12} | {obs:.4f}   | {pred:.4f}   | {err:.2f}%")

if __name__ == "__main__":
    run_final_ckm_model()
