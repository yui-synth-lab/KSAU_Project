import numpy as np
from sklearn.linear_model import LinearRegression

def analyze_ckm_full():
    # Topology Volumes from data
    vol = {
        'Up': 6.5517, 'Charm': 11.5171, 'Top': 15.3600,
        'Down': 7.3277, 'Strange': 9.5319, 'Bottom': 12.2763
    }
    
    # Experimental CKM (PDG 2022 magnitudes)
    ckm_exp = np.array([
        [0.9743, 0.2253, 0.0036],
        [0.2252, 0.9734, 0.0410],
        [0.0086, 0.0400, 0.9991]
    ])
    
    up_type = ['Up', 'Charm', 'Top']
    down_type = ['Down', 'Strange', 'Bottom']
    
    d_vols = []
    ln_vij = []
    
    print(f"{'Transition':<10} | {'dVol':<10} | {'Exp':<10} | {'ln(Exp)':<10}")
    print("-" * 50)
    for i, u in enumerate(up_type):
        for j, d in enumerate(down_type):
            dv = abs(vol[u] - vol[d])
            val = ckm_exp[i, j]
            d_vols.append(dv)
            ln_vij.append(np.log(val))
            print(f"{u+'->'+d:<10} | {dv:<10.4f} | {val:<10.4f} | {np.log(val):<10.4f}")
            
    # Regression
    X = np.array(d_vols).reshape(-1, 1)
    y = np.array(ln_vij)
    reg = LinearRegression().fit(X, y)
    
    r2 = reg.score(X, y)
    slope = reg.coef_[0]
    
    print("-" * 50)
    print(f"Regression Slope : {slope:.4f} (Theoretical: -0.5000)")
    print(f"Correlation R^2  : {r2:.4f}")
    
    # Check u->s specifically again
    dv_us = abs(vol['Up'] - vol['Strange'])
    pred_us = np.exp(-0.5 * dv_us)
    print("\nSpecific Prediction for u->s (Cabibbo):")
    print(f"  dVol      : {dv_us:.4f}")
    print(f"  Predicted : {pred_us:.4f}")
    print(f"  Exp       : 0.2253")
    print(f"  Error     : {(pred_us - 0.2253)/0.2253*100:.3f}%")

if __name__ == "__main__":
    analyze_ckm_full()