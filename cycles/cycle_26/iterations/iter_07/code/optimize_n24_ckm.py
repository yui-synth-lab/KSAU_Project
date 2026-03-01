
import numpy as np
import pandas as pd
import sys
from pathlib import Path
import re
from scipy.optimize import minimize

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
    
    quarks = ["Up", "Charm", "Top", "Down", "Strange", "Bottom"]
    quark_data = {}
    for qk in quarks:
        topo_info = topo_assignments[qk]
        name = topo_info['topology'].split('{')[0]
        row = knots_df[knots_df['name'] == name]
        if row.empty: row = links_df[links_df['name'] == name]
        if row.empty: row = links_df[links_df['name'].str.startswith(name + "{")]
        row = row.iloc[0]
        poly = row['jones_polynomial']
        j24 = get_jones_mag(poly, 24)
        quark_data[qk] = {
            'V': float(row['volume']),
            'lnJ': np.log(max(1e-10, j24))
        }

    up_types = ["Up", "Charm", "Top"]
    down_types = ["Down", "Strange", "Bottom"]
    ckm_exp = np.array(consts['ckm_matrix']['V_ij'])
    
    # Target: logit(V_ij)
    logit_exp = np.log(ckm_exp / (1.0 - ckm_exp))
    
    # X matrix: [1, dV, dlnJ, 1/V_bar, dV*dlnJ]
    X = []
    y = []
    for i, u in enumerate(up_types):
        for j, d in enumerate(down_types):
            udata = quark_data[u]
            ddata = quark_data[d]
            dV = abs(udata['V'] - ddata['V'])
            dlnJ = abs(udata['lnJ'] - ddata['lnJ'])
            v_bar = (udata['V'] + ddata['V']) / 2.0
            X.append([1.0, dV, dlnJ, 1.0/v_bar, dV * dlnJ])
            y.append(logit_exp[i, j])
    
    X = np.array(X)
    y = np.array(y)
    
    # Linear Regression to find coefficients
    coeffs, residuals, rank, s = np.linalg.lstsq(X, y, rcond=None)
    
    C, A, B, beta, gamma = coeffs
    
    print(f"Optimized Coefficients (n=24):")
    print(f"A: {A:.4f}, B: {B:.4f}, beta: {beta:.4f}, gamma: {gamma:.4f}, C: {C:.4f}")
    
    # LOO-CV
    errors_loo = []
    for i in range(len(y)):
        X_train = np.delete(X, i, axis=0)
        y_train = np.delete(y, i, axis=0)
        X_test = X[i].reshape(1, -1)
        y_test = y[i]
        
        c_loo, _, _, _ = np.linalg.lstsq(X_train, y_train, rcond=None)
        y_pred = np.dot(X_test, c_loo)[0]
        
        # Convert back to V_ij
        v_obs = 1.0 / (1.0 + np.exp(-y_test))
        v_pred = 1.0 / (1.0 + np.exp(-y_pred))
        err = abs(v_obs - v_pred) / v_obs * 100
        errors_loo.append(err)
        
    print(f"\nLOO-CV Mean Relative Error: {np.mean(errors_loo):.2f}%")
    
    # Compare with geometric candidates
    pi = np.pi
    alpha_inv = 137.036
    sin2w = 0.23122
    
    print(f"\nGeometric Constants Comparison:")
    print(f"A: {A:.4f} vs {-2*pi:.4f} (diff: {abs(A+2*pi):.4f})")
    print(f"B: {B:.4f} vs {4*pi:.4f} (diff: {abs(B-4*pi):.4f})")
    print(f"beta: {beta:.4f} vs {-alpha_inv*(1-sin2w):.4f} (diff: {abs(beta+alpha_inv*(1-sin2w)):.4f})")
    print(f"C: {C:.4f} vs {np.exp(pi)+0.1:.4f} (diff: {abs(C-(np.exp(pi)+0.1)):.4f})")

if __name__ == "__main__":
    main()
