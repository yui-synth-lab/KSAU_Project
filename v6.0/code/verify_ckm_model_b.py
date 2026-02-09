import numpy as np
import pandas as pd
import ksau_config
from sklearn.linear_model import LinearRegression
import scipy.stats as stats

def verify_ckm_model_b():
    print("="*80)
    print("KSAU v6.0: CKM Model B Validation (Tunneling Anomaly)")
    print("="*80)

    # 1. Load Data
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
            ln_v = np.log(val)
            
            data.append({
                'transition': f"{u_name}->{d_name}",
                'dV': dv,
                'Vbar': vbar,
                'dGen': dgen,
                'lnV': ln_v,
                'Vbar_inv': 1.0 / vbar if vbar > 0 else 0
            })

    df = pd.DataFrame(data)

    # 2. Regression Model A: dV only
    X_a = df[['dV']]
    y = df['lnV']
    reg_a = LinearRegression().fit(X_a, y)
    r2_a = reg_a.score(X_a, y)
    print(f"Model A (dV only) R^2: {r2_a:.4f}")

    # 3. Regression Model B: dV + 1/Vbar (Tunneling)
    X_b = df[['dV', 'Vbar_inv']]
    reg_b = LinearRegression().fit(X_b, y)
    r2_b = reg_b.score(X_b, y)
    print(f"Model B (dV + 1/Vbar) R^2: {r2_b:.4f}")

    # 4. Partial Correlations (controlling for dGen)
    print("\n[PARTIAL CORRELATIONS]")
    
    def partial_corr(x_name, y_col, control_name):
        # Linear regression of y on control
        ctrl_X = df[[control_name]]
        res_y = y_col - LinearRegression().fit(ctrl_X, y_col).predict(ctrl_X).flatten()
        # Linear regression of x on control
        res_x = df[x_name].values - LinearRegression().fit(ctrl_X, df[x_name]).predict(ctrl_X).flatten()
        r, p = stats.pearsonr(res_x, res_y)
        return r, p

    r_dv, p_dv = partial_corr('dV', df['lnV'], 'dGen')
    r_vbar, p_vbar = partial_corr('Vbar_inv', df['lnV'], 'dGen')
    
    print(f"ln|V| vs dV (ctrl dGen)   : r = {r_dv:.3f}, p = {p_dv:.4f}")
    print(f"ln|V| vs 1/Vbar (ctrl dGen): r = {r_vbar:.3f}, p = {p_vbar:.4f}")

    # 5. Combined Interaction Model (dV * 1/Vbar)
    df['Interaction'] = df['dV'] * df['Vbar_inv']
    X_c = df[['dV', 'Vbar_inv', 'Interaction']]
    reg_c = LinearRegression().fit(X_c, y)
    r2_c = reg_c.score(X_c, y)
    print(f"\nModel C (dV + 1/Vbar + Interaction) R^2: {r2_c:.4f}")

    # 6. Model with dGen directly
    X_dgen = df[['dV', 'Vbar_inv', 'dGen']]
    reg_dgen = LinearRegression().fit(X_dgen, y)
    r2_dgen = reg_dgen.score(X_dgen, y)
    print(f"Model with dGen (dV + 1/Vbar + dGen) R^2: {r2_dgen:.4f}")

    print("\nCONCLUSION:")
    if r2_dgen > 0.85:
        print(f"SUCCESS: Model with topological variables and generation gap reached R^2 = {r2_dgen:.4f}.")
    else:
        print(f"R^2 is {r2_dgen:.4f}. Trying the ΔV·V̄ interaction mentioned in report...")
        df['dV_Vbar'] = df['dV'] * df['Vbar']
        X_rep = df[['dV', 'Vbar', 'dV_Vbar']]
        reg_rep = LinearRegression().fit(X_rep, y)
        print(f"Interaction Model (dV, Vbar, dV*Vbar) R^2: {reg_rep.score(X_rep, y):.4f}")

if __name__ == "__main__":
    verify_ckm_model_b()
