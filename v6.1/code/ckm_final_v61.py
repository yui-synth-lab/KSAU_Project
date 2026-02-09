import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import utils_v61

def run_final_ckm_model():
    print("="*60)
    print("KSAU v6.1: Final CKM Model (Log-Interference)")
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
        quarks[q_name] = {
            'V': float(row['volume']),
            'J': abs(jones_val),
            'ln_J': np.log(abs(jones_val))
        }

    # 3. Experimental Data
    ckm_exp = {
        ('Up', 'Down'): 0.9743, ('Up', 'Strange'): 0.2253, ('Up', 'Bottom'): 0.0036,
        ('Charm', 'Down'): 0.2252, ('Charm', 'Strange'): 0.9734, ('Charm', 'Bottom'): 0.0410,
        ('Top', 'Down'): 0.0086, ('Top', 'Strange'): 0.0400, ('Top', 'Bottom'): 0.9991
    }

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
