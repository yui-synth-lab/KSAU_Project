import numpy as np
import pandas as pd
import ksau_config
from sklearn.linear_model import LinearRegression
import scipy.stats as stats

def calculate_off_diagonal_stats():
    topo = ksau_config.load_topology_assignments()
    phys = ksau_config.load_physical_constants()
    ckm_exp = np.array(phys['ckm']['matrix'])

    up_type = ['Up', 'Charm', 'Top']
    down_type = ['Down', 'Strange', 'Bottom']

    data = []
    for i, u_name in enumerate(up_type):
        for j, d_name in enumerate(down_type):
            if i == j: continue # OFF-DIAGONAL ONLY
            
            u_info = topo[u_name]
            d_info = topo[d_name]
            dv = abs(u_info['volume'] - d_info['volume'])
            vbar = (u_info['volume'] + d_info['volume']) / 2.0
            dgen = abs(u_info['generation'] - d_info['generation'])
            val = ckm_exp[i, j]
            data.append({'dv': dv, 'vbar': vbar, 'dgen': dgen, 'lnv': np.log(val)})

    df = pd.DataFrame(data)
    df['vbar_inv'] = 1.0 / df['vbar']

    print("--- OFF-DIAGONAL Partial Correlations (ctrl dgen) ---")
    for col in ['dv', 'vbar', 'vbar_inv']:
        X = df[['dgen']]
        ry = df['lnv'] - LinearRegression().fit(X, df['lnv']).predict(X)
        rx = df[col] - LinearRegression().fit(X, df[col]).predict(X)
        r, p = stats.pearsonr(rx, ry)
        print(f"ln|V| vs {col:12}: r = {r:+.4f}, p = {p:.4f}")

    print("\n--- OFF-DIAGONAL Regression Models ---")
    X_a = df[['dv', 'dgen']]
    reg_a = LinearRegression().fit(X_a, df['lnv'])
    print(f"Model (dv, dgen) R^2: {reg_a.score(X_a, df['lnv']):.4f}")

    X_b = df[['dv', 'vbar_inv', 'dgen']]
    reg_b = LinearRegression().fit(X_b, df['lnv'])
    print(f"Model (dv, vbar_inv, dgen) R^2: {reg_b.score(X_b, df['lnv']):.4f}")

if __name__ == "__main__":
    calculate_off_diagonal_stats()