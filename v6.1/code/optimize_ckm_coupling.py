import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import utils_v61

def optimize_ckm_coupling():
    print("="*60)
    print("KSAU v6.1: CKM Coupling Constant Optimization")
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
    print("Loading Quark Topology Data...")
    for q_name, topo_name in quark_map.items():
        row = links[links['name'] == topo_name]
        if row.empty:
             row = links[links['name'].str.startswith(topo_name + "{")]
        
        if row.empty:
            continue
        row = row.iloc[0]
        
        vol = float(row['volume'])
        
        # Jones at e^(i 2pi/5)
        jones_val = utils_v61.get_jones_at_root_of_unity(row['jones_polynomial'], n=5)
        jones_mag = abs(jones_val)
        jones_log = np.log(jones_mag) if jones_mag > 0 else 0
        
        quarks[q_name] = {
            'V': vol,
            'J_mag': jones_mag,
            'ln_J': jones_log
        }

    # 3. CKM Experimental Data
    ckm_exp = {
        ('Up', 'Down'): 0.9743, ('Up', 'Strange'): 0.2253, ('Up', 'Bottom'): 0.0036,
        ('Charm', 'Down'): 0.2252, ('Charm', 'Strange'): 0.9734, ('Charm', 'Bottom'): 0.0410,
        ('Top', 'Down'): 0.0086, ('Top', 'Strange'): 0.0400, ('Top', 'Bottom'): 0.9991
    }

    # 4. Define Models to Test
    models = [
        {
            'name': 'Linear Jones',
            'func': lambda q1, q2: [abs(quarks[q1]['V'] - quarks[q2]['V']), abs(quarks[q1]['J_mag'] - quarks[q2]['J_mag'])]
        },
        {
            'name': 'Log Jones (Entropy)',
            'func': lambda q1, q2: [abs(quarks[q1]['V'] - quarks[q2]['V']), abs(quarks[q1]['ln_J'] - quarks[q2]['ln_J'])]
        },
        {
            'name': 'Squared Jones',
            'func': lambda q1, q2: [abs(quarks[q1]['V'] - quarks[q2]['V']), abs(quarks[q1]['J_mag'] - quarks[q2]['J_mag'])**2]
        },
        {
            'name': 'Volume Only (Baseline)',
            'func': lambda q1, q2: [abs(quarks[q1]['V'] - quarks[q2]['V'])]
        }
    ]

    best_r2 = -100
    best_model_name = ""
    best_coeffs = []
    best_preds = []
    
    y = []
    labels = []
    for (_, _), val in ckm_exp.items():
        y.append(np.log(val))
        
    y = np.array(y)

    print("\n[Model Comparison]")
    print(f"{'Model Name':<20} | {'R^2':<8} | {'Coeff A (Vol)':<15} | {'Coeff B (Topo)'}")
    print("-" * 70)

    for model in models:
        X = []
        labels = [] # Reset labels to match order
        for (q1, q2), val in ckm_exp.items():
            X.append(model['func'](q1, q2))
            labels.append(f"{q1}-{q2}")
            
        X = np.array(X)
        
        reg = LinearRegression()
        reg.fit(X, y)
        r2 = reg.score(X, y)
        
        coeffs = reg.coef_
        intercept = reg.intercept_
        
        a_val = f"{coeffs[0]:.4f}"
        b_val = f"{coeffs[1]:.4f}" if len(coeffs) > 1 else "N/A"
        
        print(f"{model['name']:<20} | {r2:.4f}   | {a_val:<15} | {b_val}")
        
        if r2 > best_r2:
            best_r2 = r2
            best_model_name = model['name']
            best_coeffs = coeffs
            best_intercept = intercept
            best_preds = reg.predict(X)

    # 5. Detail Analysis of Best Model
    print(f"\n[Best Model Details: {best_model_name}]")
    print(f"R^2: {best_r2:.6f}")
    print(f"Intercept: {best_intercept:.4f}")
    
    print("\nPredictions:")
    print(f"{'Pair':<12} | {'Observed':<8} | {'Predicted':<8} | {'Error %':<8}")
    
    total_log_err = 0
    for i, label in enumerate(labels):
        obs = np.exp(y[i])
        pred = np.exp(best_preds[i])
        err_pct = abs(obs - pred) / obs * 100
        
        print(f"{label:<12} | {obs:.4f}   | {pred:.4f}    | {err_pct:.2f}%")

    # 6. Grid Search for Manual Tuning (if Linear Regression didn't find the physical "sweet spot")
    # Sometimes regression fits noise. Let's check if fixed physical constants work better.
    # Theoretical Hypothesis: A = -0.5 (Geometric), B = ?
    
    if "Log Jones" in best_model_name:
        print("\n[Theoretical Tuning: Fixed A = -0.5]")
        # Fix A = -0.5, find best B
        # ln|V| = -0.5 * dV + B * d(lnJ) + C
        # ln|V| + 0.5 * dV = B * d(lnJ) + C
        
        X_fixed = []
        Y_fixed = []
        
        for (q1, q2), val in ckm_exp.items():
            dV = abs(quarks[q1]['V'] - quarks[q2]['V'])
            dlnJ = abs(quarks[q1]['ln_J'] - quarks[q2]['ln_J'])
            
            target = np.log(val) + 0.5 * dV
            X_fixed.append([dlnJ])
            Y_fixed.append(target)
            
        X_fixed = np.array(X_fixed)
        Y_fixed = np.array(Y_fixed)
        
        reg_fix = LinearRegression()
        reg_fix.fit(X_fixed, Y_fixed)
        
        b_fixed = reg_fix.coef_[0]
        c_fixed = reg_fix.intercept_
        r2_fixed = reg_fix.score(X_fixed, Y_fixed) # This R2 is for the residual, not original y
        
        # Simpler: Re-predict
        preds_Y = []
        obs_Y = []
        for (q1, q2), val in ckm_exp.items():
            dV = abs(quarks[q1]['V'] - quarks[q2]['V'])
            dlnJ = abs(quarks[q1]['ln_J'] - quarks[q2]['ln_J'])
            pred_log = -0.5 * dV + b_fixed * dlnJ + c_fixed
            preds_Y.append(pred_log)
            obs_Y.append(np.log(val))
            
        preds_Y = np.array(preds_Y)
        obs_Y = np.array(obs_Y)
        
        ss_res = np.sum((obs_Y - preds_Y)**2)
        ss_tot = np.sum((obs_Y - np.mean(obs_Y))**2)
        final_r2_fixed = 1 - (ss_res / ss_tot)
        
        print(f"Forced A = -0.5000")
        print(f"Resulting B (Entropy Coeff): {b_fixed:.4f}")
        print(f"Resulting R^2              : {final_r2_fixed:.4f}")

if __name__ == "__main__":
    optimize_ckm_coupling()
