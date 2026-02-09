import numpy as np
import pandas as pd
import ksau_config
from sklearn.linear_model import LinearRegression
import scipy.stats as stats
from itertools import combinations

def search_ckm_law():
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
            val = ckm_exp[i, j]
            data.append({'dv': dv, 'vbar': vbar, 'lnv': np.log(val)})

    df = pd.DataFrame(data)

    print("--- Correlation Search ---")
    df['interaction'] = df['dv'] * df['vbar']
    df['tunneling'] = df['dv'] / df['vbar']
    df['vbar_inv'] = 1.0 / df['vbar']
    
    for col in ['dv', 'vbar', 'interaction', 'tunneling', 'vbar_inv']:
        r, p = stats.pearsonr(df[col], df['lnv'])
        print(f"ln|V| vs {col:12}: r = {r:+.4f}, p = {p:.4f}")

    print("\n--- Model Search ---")
    features = ['dv', 'vbar', 'interaction', 'tunneling', 'vbar_inv']
    for n in range(1, 4):
        for combo in combinations(features, n):
            X = df[list(combo)]
            reg = LinearRegression().fit(X, df['lnv'])
            r2 = reg.score(X, df['lnv'])
            if r2 > 0.8:
                print(f"Model {combo} R^2: {r2:.4f}")

if __name__ == "__main__":
    search_ckm_law()