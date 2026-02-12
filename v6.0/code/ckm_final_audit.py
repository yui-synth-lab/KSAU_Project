import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import ksau_config
import re
from sympy import sympify

# ============================================================================
# UTILITIES
# ============================================================================

def parse_polynomial(poly_str, val):
    if pd.isna(poly_str): return 0.0
    # Clean and standardize string for SymPy
    s = str(poly_str).replace(' ', '').replace('t', 'x').replace('q', 'x').replace('^', '**')
    try:
        expr = sympify(s)
        return complex(expr.subs('x', val))
    except Exception:
        return 0.0

def get_jones_mag(poly_str):
    phase = np.exp(1j * 2 * np.pi / 5)
    val = parse_polynomial(poly_str, phase)
    return abs(val)

def _select_link_row(links: pd.DataFrame, topology: str) -> pd.Series:
    """
    Select the LinkInfo row matching the assigned topology.
    """
    topo = str(topology).strip()
    exact = links[links["name"] == topo]
    if not exact.empty:
        return exact.iloc[0]

    base = topo.split("{")[0]
    candidates = links[links["name"].str.startswith(base)]
    if candidates.empty:
        raise KeyError(f"Topology not found in LinkInfo: {topo}")

    return candidates.iloc[0]

# ============================================================================
# AUDIT CORE
# ============================================================================

def analyze_ckm_comprehensive_v60():
    print("="*80)
    print("KSAU v6.0 Final Audit: Comprehensive CKM Model (Logit-Geometric)")
    print("Formula: logit|Vij| = -0.5*dV + B*dlnJ + beta/V_bar + C")
    print("Logic: Enforces 0 < |Vij| < 1 (range constraint); does NOT enforce CKM unitarity.")
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
            u_row = _select_link_row(links, topo[u]["topology"])
            d_row = _select_link_row(links, topo[d]["topology"])
            u_j = get_jones_mag(u_row['jones_polynomial'])
            d_j = get_jones_mag(d_row['jones_polynomial'])
            
            v1, v2 = topo[u]['volume'], topo[d]['volume']
            dv = abs(v1 - v2)
            v_bar = (v1 + v2) / 2.0
            dlnj = abs(np.log(u_j) - np.log(d_j))
            
            # Logit transformation
            p_obs = np.clip(ckm_exp[i, j], 1e-6, 1.0 - 1e-6)
            logit_p = np.log(p_obs / (1.0 - p_obs))
            
            # Target
            target = logit_p + 0.5 * dv
            
            data.append({
                'dlnj': dlnj,
                'inv_vbar': 1.0 / v_bar,
                'dv': dv, 
                'target': target,
                'obs_val': ckm_exp[i, j],
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
    df['pred_z'] = -0.5 * df['dv'] + B * df['dlnj'] + beta * df['inv_vbar'] + C
    df['pred_val'] = 1.0 / (1.0 + np.exp(-df['pred_z']))
    
    # Calculate R2 on logit scale
    y_true_logit = np.log(df['obs_val'] / (1.0 - df['obs_val']))
    ss_res = np.sum((y_true_logit - df['pred_z'])**2)
    ss_tot = np.sum((y_true_logit - np.mean(y_true_logit))**2)
    r2 = 1 - (ss_res / ss_tot)

    print(f"Global R^2 (Logit Scale): {r2:.6f}")
    print(f"Parameters (Fixed A = -0.5):")
    print(f"  B (Entropy)      : {B:.4f}")
    print(f"  beta (Tunneling) : {beta:.4f}")
    print(f"  C (Intercept)    : {C:.4f}")

    print("\nDetailed Matrix Fit (Bounded [0, 1]):")
    print(f"{'Transition':<15} | {'Observed':<10} | {'Predicted':<10} | {'Error %'}")
    print("-" * 65)
    for i, row in df.iterrows():
        obs = row['obs_val']
        pred = row['pred_val']
        err = abs(pred - obs) / obs * 100
        print(f"{row['pair']:<15} | {obs:.4f}   | {pred:.4f}    | {err:.2f}%")

if __name__ == "__main__":
    analyze_ckm_comprehensive_v60()
