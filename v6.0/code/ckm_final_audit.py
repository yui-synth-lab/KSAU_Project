import numpy as np
import pandas as pd
import ksau_config
import re
from sympy import sympify

# ============================================================================
# UTILITIES
# ============================================================================

def parse_polynomial(poly_str, val):
    if pd.isna(poly_str): return 0.0
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
    topo = str(topology).strip()
    exact = links[links["name"] == topo]
    if not exact.empty: return exact.iloc[0]
    base = topo.split("{")[0]
    candidates = links[links["name"].str.startswith(base)]
    if candidates.empty: raise KeyError(f"Topology not found in LinkInfo: {topo}")
    return candidates.iloc[0]

# ============================================================================
# THEORETICAL AUDIT (Zero-Parameter Master Formula)
# ============================================================================

def audit_ckm_master_formula_v60():
    print("="*80)
    print("KSAU v6.0 Final Audit: Zero-Parameter Geometric Interaction Model")
    print("Status: Verifying Emergent Constants (-3pi/4, -4pi, ln(12))")
    print("="*80)

    # 1. Load Data
    phys = ksau_config.load_physical_constants()
    topo = ksau_config.load_topology_assignments()
    links = pd.read_csv(ksau_config.load_linkinfo_path(), sep='|', skiprows=[1])
    
    # 2. Geometric Moduli (Loaded from SSoT: physical_constants.json)
    # CORRECTED: Use same coefficients as topology_official_selector.py
    pi = np.pi
    alpha = phys.get('alpha_em', 0.0072973525)
    geom = phys['ckm']['geometric_coefficients']

    # Master Formula Constants (same as topology selector)
    A = geom['A_barrier_pi_factor'] * pi
    B = geom['B_complex_pi_factor'] * pi
    beta = geom['beta_visc_alpha_factor'] / alpha
    gamma = np.sqrt(geom['gamma_res_sqrt'])

    # C_drive formula: pi^2 + 2*pi
    C = (pi**2) + (2*pi)

    print(f"Moduli: A={A:.4f}, B={B:.4f}, beta={beta:.4f}, gamma={gamma:.4f}, C={C:.4f}\n")

    ckm_exp = np.array(phys['ckm']['matrix'])
    up_type = ['Up', 'Charm', 'Top']
    down_type = ['Down', 'Strange', 'Bottom']
    
    results = []
    for i, u in enumerate(up_type):
        for j, d in enumerate(down_type):
            u_row = _select_link_row(links, topo[u]["topology"])
            d_row = _select_link_row(links, topo[d]["topology"])
            u_j = get_jones_mag(u_row['jones_polynomial'])
            d_j = get_jones_mag(d_row['jones_polynomial'])
            
            v1, v2 = topo[u]['volume'], topo[d]['volume']
            dv = abs(v1 - v2)
            v_bar = (v1 + v2) / 2.0
            dlnj = abs(np.log(max(1e-10, u_j)) - np.log(max(1e-10, d_j)))
            
            # Master Formula
            logit_v = C + A*dv + B*dlnj + beta/v_bar + gamma*(dv*dlnj)
            pred = 1.0 / (1.0 + np.exp(-logit_v))
            
            results.append({
                'pair': f"{u}-{d}",
                'obs': ckm_exp[i, j],
                'pred': pred
            })

    df = pd.DataFrame(results)
    
    print(f"{'Transition':<15} | {'Observed':<10} | {'Geo-Pred':<10} | {'Error %'}")
    print("-" * 65)
    for _, row in df.iterrows():
        obs, pred = row['obs'], row['pred']
        err = abs(pred - obs) / obs * 100
        print(f"{row['pair']:<15} | {obs:.4f}   | {pred:.4f}    | {err:.2f}%")

    # Global MAE
    mae = np.mean(np.abs(df['pred'] - df['obs']))
    print("-" * 65)
    print(f"Global Theory MAE: {mae:.4e}")

if __name__ == "__main__":
    audit_ckm_master_formula_v60()
