import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import utils_v61

def run_ckm_analysis():
    print("="*60)
    print("KSAU v6.1: CKM Quantum Interference Analysis")
    print("="*60)

    # 1. Load Data, Metadata and Constants
    _, links = utils_v61.load_data()
    assignments = utils_v61.load_assignments()
    consts = utils_v61.load_constants()
    
    # 2. Extract Topologies from Central Metadata
    quark_names = ["Up", "Down", "Strange", "Charm", "Bottom", "Top"]
    quarks = {}
    
    print("Loading Quark Topology Data...")
    for q_name in quark_names:
        topo_info = assignments.get(q_name)
        if not topo_info:
            continue
            
        topo_name = topo_info['topology'].split('{')[0] # Get base name
        row = links[links['name'] == topo_name]
        if row.empty:
             row = links[links['name'].str.startswith(topo_name + "{")]
        
        if row.empty:
            print(f"CRITICAL ERROR: Could not find topology {topo_name} for {q_name}")
            continue
            
        row = row.iloc[0]
        
        # Get Volume
        vol = float(row['volume'])
        
        # Get Jones at e^(i 2pi/5)
        jones_poly = row['jones_polynomial']
        jones_val = utils_v61.get_jones_at_root_of_unity(jones_poly, n=5)
        jones_mag = abs(jones_val)
        
        quarks[q_name] = {
            'V': vol,
            'J_mag': jones_mag,
            'topo': row['name']
        }
        print(f"  {q_name:8} | {row['name']:10} | Vol: {vol:.4f} | |J(5)|: {jones_mag:.4f}")

    # 3. CKM Experimental Data from Central Constants
    ckm_matrix = consts['ckm']['matrix']
    up_types = ["Up", "Charm", "Top"]
    down_types = ["Down", "Strange", "Bottom"]
    
    ckm_exp = {}
    for i, u in enumerate(up_types):
        for j, d in enumerate(down_types):
            ckm_exp[(u, d)] = ckm_matrix[i][j]

    # 4. Prepare Regression Data
    # Formula: ln|Vij| = A * dV + B * d|J| + C
    
    X = []
    y = []
    labels = []
    
    for (q1, q2), val in ckm_exp.items():
        d_vol = abs(quarks[q1]['V'] - quarks[q2]['V'])
        d_jones = abs(quarks[q1]['J_mag'] - quarks[q2]['J_mag'])
        
        X.append([d_vol, d_jones])
        y.append(np.log(val))
        labels.append(f"{q1}-{q2}")
        
    X = np.array(X)
    y = np.array(y)
    
    # 5. Fit Model
    reg = LinearRegression()
    reg.fit(X, y)
    
    r2 = reg.score(X, y)
    preds = reg.predict(X)
    
    # 6. Output Results
    print("\n--- Model Results ---")
    print(f"Formula: ln|Vij| = A * dV_hyp + B * d|J(2pi/5)| + C")
    print(f"A (Volume Coeff): {reg.coef_[0]:.4f}")
    print(f"B (Jones Coeff) : {reg.coef_[1]:.4f}")
    print(f"C (Intercept)   : {reg.intercept_:.4f}")
    print(f"R^2             : {r2:.6f}")
    
    print("\n--- Predictions vs Observed ---")
    print(f"{'Pair':<12} | {'Observed':<8} | {'Predicted':<8} | {'Error %':<8}")
    for i, label in enumerate(labels):
        obs = np.exp(y[i])
        pred = np.exp(preds[i])
        err = abs(obs - pred) / obs * 100
        print(f"{label:<12} | {obs:.4f}   | {pred:.4f}    | {err:.2f}%")

if __name__ == "__main__":
    run_ckm_analysis()
