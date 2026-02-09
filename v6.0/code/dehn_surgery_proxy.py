import numpy as np
import ksau_config
import matplotlib.pyplot as plt

def analyze_dehn_proxy():
    print("="*80)
    print("KSAU v6.1 Exploration: Dehn Surgery Proxy Analysis")
    print("Testing if 'Surgery Distance' explains CKM hierarchy better than 'Generation Penalty'")
    print("="*80)

    # 1. Load Data
    topo_assignments = ksau_config.load_topology_assignments()
    phys_constants = ksau_config.load_physical_constants()
    ckm_exp = np.array(phys_constants['ckm']['matrix'])
    
    # Define mapping
    key_map = {
        'u': 'Up', 'c': 'Charm', 't': 'Top',
        'd': 'Down', 's': 'Strange', 'b': 'Bottom'
    }

    # Extract Particle Attributes
    quarks = {}
    for k, name in key_map.items():
        data = topo_assignments[name]
        quarks[k] = {
            'Vol': data['volume'],
            'N': data['crossing_number'], # Proxy for Surgery Complexity
            'Comp': data['components'],   # Link components
            'Name': name
        }

    # 2. Define Transition Data Points
    transitions = []
    up_type = ['u', 'c', 't']
    down_type = ['d', 's', 'b']
    
    data_points = []

    for i, u_k in enumerate(up_type):
        for j, d_k in enumerate(down_type):
            u = quarks[u_k]
            d = quarks[d_k]
            
            exp_val = ckm_exp[i, j]
            
            # Metric 1: Pure Volume Difference (v6.0 Baseline)
            d_vol = abs(u['Vol'] - d['Vol'])
            
            # Metric 2: Crossing Number Difference (Surgery Proxy)
            # Concept: Changing N requires multiple crossing changes (surgeries)
            d_cross = abs(u['N'] - d['N'])
            
            # Metric 3: Component Difference penalty
            # Changing components (2->3) is a drastic topological surgery
            d_comp = abs(u['Comp'] - d['Comp'])

            data_points.append({
                'label': f"{u_k}->{d_k}",
                'exp_log': np.log(exp_val),
                'd_vol': d_vol,
                'd_cross': d_cross,
                'd_comp': d_comp,
                'exp_val': exp_val
            })

    # 3. Model Testing
    import pandas as pd
    df = pd.DataFrame(data_points)

    print("\n--- Model A: Pure Volume (v6.0 Baseline) ---")
    # ln|V| = a * dVol + b
    coeffs_a = np.polyfit(df['d_vol'], df['exp_log'], 1)
    pred_a = np.polyval(coeffs_a, df['d_vol'])
    r2_a = 1 - np.sum((df['exp_log'] - pred_a)**2) / np.sum((df['exp_log'] - df['exp_log'].mean())**2)
    print(f"Equation: ln|V| = {coeffs_a[0]:.4f} * dVol + {coeffs_a[1]:.4f}")
    print(f"R-squared: {r2_a:.4f}")

    print("\n--- Model B: Surgery Proxy (dVol + dCrossing) ---")
    # Hypothesis: Cost = k1 * dVol + k2 * dCrossing
    # We use simple linear regression on two variables
    X = np.column_stack((df['d_vol'], df['d_cross']))
    y = df['exp_log']
    
    # Solve for coeffs: y = k1*x1 + k2*x2 + c
    from sklearn.linear_model import LinearRegression
    model_b = LinearRegression()
    model_b.fit(X, y)
    r2_b = model_b.score(X, y)
    
    k1, k2 = model_b.coef_
    intercept = model_b.intercept_
    
    print(f"Equation: ln|V| = {k1:.4f} * dVol + {k2:.4f} * dCrossing + {intercept:.4f}")
    print(f"R-squared: {r2_b:.4f}")
    print("Interpretation:")
    print(f"  Volume Coeff (Energy Cost)     : {k1:.4f} (v6.0 theory: -0.5)")
    print(f"  Crossing Coeff (Surgery Cost)  : {k2:.4f} (Suppression per crossing change)")

    # 4. Detailed Comparison
    print("\n[Prediction Audit]")
    print(f"{'Transition':<10} | {'Exp':<8} | {'Model A (Vol)':<12} | {'Model B (Surg)':<12} | {'Improvement'}")
    print("-" * 70)
    
    pred_b_vals = np.exp(model_b.predict(X))
    pred_a_vals = np.exp(pred_a)
    
    for i, row in df.iterrows():
        p_a = pred_a_vals[i]
        p_b = pred_b_vals[i]
        exp = row['exp_val']
        
        err_a = abs(p_a - exp) / exp
        err_b = abs(p_b - exp) / exp
        improved = "YES" if err_b < err_a else "NO"
        
        print(f"{row['label']:<10} | {exp:<8.4f} | {p_a:<12.4f} | {p_b:<12.4f} | {improved}")

    print("="*80)
    print("CONCLUSION:")
    if r2_b > 0.8:
        print("  SUCCESS: Adding 'Surgery Cost' (Crossing Difference) significantly explains the hierarchy.")
        print(f"  This replaces the ad-hoc generation parameter 'n' with physically meaningful 'Delta N'.")
        print(f"  The suppression per unit crossing change is exp({k2:.2f}) approx 1/{np.exp(-k2):.1f}.")
    else:
        print("  PARTIAL: Crossing difference improves fit but doesn't solve everything.")
    print("="*80)

if __name__ == "__main__":
    analyze_dehn_proxy()
