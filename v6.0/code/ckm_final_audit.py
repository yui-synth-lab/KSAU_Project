import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import ksau_config
import re

def parse_polynomial(poly_str, val):
    if pd.isna(poly_str): return 0.0
    poly_str = str(poly_str).replace(' ', '').replace('t', 'x').replace('q', 'x')
    expr = poly_str.replace('^', '**')
    x = val
    try:
        clean_expr = re.sub(r'x[0-9]+', 'x', expr)
        return eval(clean_expr)
    except:
        return 0.0

def get_jones_mag(poly_str):
    phase = np.exp(1j * 2 * np.pi / 5)
    val = parse_polynomial(poly_str, phase)
    return abs(val)

def analyze_ckm_comprehensive_v60():
    print("="*80)
    print("KSAU v6.0 Final Audit: Comprehensive CKM Model (Tunneling + Entropy)")
    print("Formula: ln|Vij| = -0.5*dV + B*dlnJ + beta/V_bar + C")
    print("="*80)

    # 1. Load Data
    phys = ksau_config.load_physical_constants()
    topo = ksau_config.load_topology_assignments()
    link_path = ksau_config.load_linkinfo_path()
    links = pd.read_csv(link_path, sep='|', skiprows=[1])
    
    ckm_exp = np.array(phys['ckm']['matrix'])
    up_type = ['Up', 'Charm', 'Top']
    down_type = ['Down', 'Strange', 'Bottom']
    
    # 2. Extract Data
    data = []
    for i, u in enumerate(up_type):
        for j, d in enumerate(down_type):
            u_base = topo[u]['topology'].split('{')[0]
            d_base = topo[d]['topology'].split('{')[0]
            u_row = links[links['name'].str.startswith(u_base)].iloc[0]
            d_row = links[links['name'].str.startswith(d_base)].iloc[0]
            u_j = get_jones_mag(u_row['jones_polynomial'])
            d_j = get_jones_mag(d_row['jones_polynomial'])
            
            v1, v2 = topo[u]['volume'], topo[d]['volume']
            dv = abs(v1 - v2)
            v_bar = (v1 + v2) / 2.0
            dlnj = abs(np.log(u_j) - np.log(d_j))
            
            target = np.log(ckm_exp[i, j]) + 0.5 * dv
            
            data.append({
                'dlnj': dlnj,
                'inv_vbar': 1.0 / v_bar,
                'dv': dv, 
                'target': target,
                'lnv_obs': np.log(ckm_exp[i, j]),
                'pair': f"{u}-{d}"
            })

    df = pd.DataFrame(data)
    X = df[['dlnj', 'inv_vbar']]
    y = df['target']
    
    reg = LinearRegression().fit(X, y)
    B = reg.coef_[0]
    beta = reg.coef_[1]
    C = reg.intercept_
    
    # Predictions
    df['pred_log'] = -0.5 * df['dv'] + B * df['dlnj'] + beta * df['inv_vbar'] + C
    preds = np.exp(df['pred_log'])
    obs = np.exp(df['lnv_obs'])
    
    r2 = 1 - (np.sum((df['lnv_obs'] - df['pred_log'])**2) / np.sum((df['lnv_obs'] - np.mean(df['lnv_obs']))**2))

    print(f"Global R^2: {r2:.6f}")
    print(f"Parameters (Fixed A = -0.5):")
    print(f"  B (Entropy)      : {B:.4f}")
    print(f"  beta (Tunneling) : {beta:.4f}")
    print(f"  C (Intercept)    : {C:.4f}")

    print("\nDetailed Matrix Fit:")
    print(f"{'Transition':<15} | {'Observed':<10} | {'Predicted':<10} | {'Error %'}")
    print("-" * 65)
    for i, row in df.iterrows():
        err = abs(preds[i] - obs[i]) / obs[i] * 100
        print(f"{row['pair']:<15} | {obs[i]:.4f}   | {preds[i]:.4f}    | {err:.2f}%")

if __name__ == "__main__":
    analyze_ckm_comprehensive_v60()
