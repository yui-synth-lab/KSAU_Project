import numpy as np
import pandas as pd
import ksau_config
from sklearn.linear_model import LinearRegression
import scipy.stats as stats

def calculate_partial_r():
    topo = ksau_config.load_topology_assignments()
    phys = ksau_config.load_physical_constants()
    ckm_exp = np.array(phys['ckm']['matrix'])

    up_type = ['Up', 'Charm', 'Top']
    down_type = ['Down', 'Strange', 'Bottom']

    data = []
    for i, u_name in enumerate(up_type):
        for j, d_name in enumerate(down_type):
            u_info = topo[u_name]
            d_info = topo[d_name]
            dv = abs(u_info['volume'] - d_info['volume'])
            vbar = (u_info['volume'] + d_info['volume']) / 2.0
            dgen = abs(u_info['generation'] - d_info['generation'])
            val = ckm_exp[i, j]
            data.append({'dv': dv, 'vbar': vbar, 'dgen': dgen, 'lnv': np.log(val)})

    df = pd.DataFrame(data)
    df['tunneling'] = df['dv'] / df['vbar']

    def partial_corr(x_name, y_name, ctrl_name):
        X = df[[ctrl_name]]
        ry = df[y_name] - LinearRegression().fit(X, df[y_name]).predict(X)
        rx = df[x_name] - LinearRegression().fit(X, df[x_name]).predict(X)
        return stats.pearsonr(rx, ry)

    print("--- Partial Correlations (ctrl dgen) ---")
    for col in ['dv', 'vbar', 'tunneling']:
        r, p = partial_corr(col, 'lnv', 'dgen')
        print(f"ln|V| vs {col:12}: r = {r:+.4f}, p = {p:.4f}")

    print("\n--- Regression Models ---")
    X_a = df[['dv', 'dgen']]
    reg_a = LinearRegression().fit(X_a, df['lnv'])
    print(f"Model (dv, dgen) R^2: {reg_a.score(X_a, df['lnv']):.4f}")

    X_b = df[['dv', 'vbar', 'dgen']]
    reg_b = LinearRegression().fit(X_b, df['lnv'])
    print(f"Model (dv, vbar, dgen) R^2: {reg_b.score(X_b, df['lnv']):.4f}")

    X_c = df[['tunneling', 'dgen']]
    reg_c = LinearRegression().fit(X_c, df['lnv'])
    print(f"Model (tunneling, dgen) R^2: {reg_c.score(X_c, df['lnv']):.4f}")

if __name__ == "__main__":
    calculate_partial_r()