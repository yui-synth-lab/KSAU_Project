
import numpy as np
import pandas as pd
import sys
from pathlib import Path
import re
import json

# Setup SSOT
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
ssot_path = project_root / "ssot"
sys.path.insert(0, str(ssot_path))    
from ksau_ssot import SSOT

def parse_polynomial(poly_str, val):
    if pd.isna(poly_str): return 0.0
    poly_str = str(poly_str).replace(' ', '').replace('t', 'x').replace('q', 'x')
    expr = poly_str.replace('^', '**')
    x = val
    try:
        clean_expr = re.sub(r'x[0-9]+', 'x', expr)
        return eval(clean_expr)
    except: return 0.0

def get_jones_mag(poly_str, n):
    phase = np.exp(1j * 2 * np.pi / n)
    val = parse_polynomial(poly_str, phase)
    return abs(val)

def main():
    ssot = SSOT()
    consts = ssot.constants()
    knots_df, links_df = ssot.knot_data()
    topo_assignments = ssot.topology_assignments()
    
    # 1. Compare ln|J| at n=5 vs n=24
    quarks = ["Up", "Charm", "Top", "Down", "Strange", "Bottom"]
    quark_data = {}
    
    for qk in quarks:
        topo_info = topo_assignments[qk]
        name = topo_info['topology'].split('{')[0]
        row = knots_df[knots_df['name'] == name]
        if row.empty:
            row = links_df[links_df['name'] == name]
        if row.empty:
            row = links_df[links_df['name'].str.startswith(name + "{")]
        
        row = row.iloc[0]
        poly = row['jones_polynomial']
        
        j5 = get_jones_mag(poly, 5)
        j24 = get_jones_mag(poly, 24)
        
        quark_data[qk] = {
            'V': float(row['volume']),
            'lnJ5': np.log(max(1e-10, j5)),
            'lnJ24': np.log(max(1e-10, j24))
        }
        print(f"{qk:7}: V={quark_data[qk]['V']:6.2f}, lnJ5={quark_data[qk]['lnJ5']:6.2f}, lnJ24={quark_data[qk]['lnJ24']:6.2f}")

    # 2. Geometric Constants Test
    pi = np.pi
    alpha_inv = 1.0 / consts['physical_constants']['alpha_em']
    sin2w = consts['physical_constants']['sin2theta_w']
    
    # Pure Geometric Coefficients
    pi = np.pi
    alpha_inv = 137.036
    sin2w = 0.23122
    A_geo = -2 * pi
    B_geo = 4 * pi
    beta_geo = -alpha_inv * (1 - sin2w)
    gamma_geo = 9.0 / 8.0
    C_geo = np.exp(pi) + 0.1
    
    print(f"\nPure Geometric Coefficients:")
    print(f"A: {A_geo:.4f}, B: {B_geo:.4f}, beta: {beta_geo:.4f}, gamma: {gamma_geo:.4f}, C: {C_geo:.4f}")
    
    # CKM matrix
    ckm_exp = np.array(consts['ckm_matrix']['V_ij'])
    up_types = ["Up", "Charm", "Top"]
    down_types = ["Down", "Strange", "Bottom"]
    
    def predict(u, d, n_mode='24'):
        udata = quark_data[u]
        ddata = quark_data[d]
        dV = abs(udata['V'] - ddata['V'])
        lnJ_u = udata['lnJ24'] if n_mode == '24' else udata['lnJ5']
        lnJ_d = ddata['lnJ24'] if n_mode == '24' else ddata['lnJ5']
        dlnJ = abs(lnJ_u - lnJ_d)
        v_bar = (udata['V'] + ddata['V']) / 2.0
        
        logit = C_geo + A_geo * dV + B_geo * dlnJ + beta_geo / v_bar + gamma_geo * (dV * dlnJ)
        return 1.0 / (1.0 + np.exp(-logit))

    print(f"\nResults with n=5 and SSoT Constants:")
    preds = []
    obs_flat = []
    errors = []
    for i, u in enumerate(up_types):
        for j, d in enumerate(down_types):
            obs = ckm_exp[i, j]
            pred = predict(u, d, '5')
            preds.append(pred)
            obs_flat.append(obs)
            err = abs(obs - pred) / obs * 100
            errors.append(err)
            print(f"{u}-{d:7}: Exp={obs:.4f}, Pred={pred:.4f}, Error={err:6.2f}%")
    
    # Calculate R2
    ss_res = np.sum((np.array(obs_flat) - np.array(preds))**2)
    ss_tot = np.sum((np.array(obs_flat) - np.mean(obs_flat))**2)
    r2 = 1 - (ss_res / ss_tot)
    
    print(f"\nMean Error: {np.mean(errors):.2f}%")
    print(f"R2: {r2:.4f}")

if __name__ == "__main__":
    main()
