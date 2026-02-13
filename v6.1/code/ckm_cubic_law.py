"""
CKM Cubic Suppression Law (Upgrade Log Section 4)
Formula: |V_ij| ∝ (J_light/J_heavy)^3 * exp(-k * dV)
Test if this achieves R^2 = 0.67 as claimed
"""
import numpy as np
import pandas as pd
import utils_v61
from scipy.optimize import minimize
from sklearn.metrics import r2_score

def model_cubic(params, J_light, J_heavy, dV):
    """
    Cubic suppression: V_ij = A * (J_light/J_heavy)^3 * exp(-k * dV)
    params: [A, k]
    """
    A, k = params
    J_ratio = J_light / (J_heavy + 1e-10)  # Avoid division by zero
    V_pred = A * (J_ratio**3) * np.exp(-k * dV)
    # Clip to [0, 1]
    V_pred = np.clip(V_pred, 1e-10, 1 - 1e-10)
    return V_pred

def model_cubic_log(params, J_light, J_heavy, dV):
    """
    Log-cubic: ln(V_ij) = C + 3*ln(J_light/J_heavy) - k*dV
    params: [k, C]
    """
    k, C = params
    J_ratio = J_light / (J_heavy + 1e-10)
    ln_pred = C + 3 * np.log(J_ratio + 1e-10) - k * dV
    V_pred = np.exp(ln_pred)
    V_pred = np.clip(V_pred, 1e-10, 1 - 1e-10)
    return V_pred

def test_cubic_law():
    """
    Test the Cubic Suppression Law
    """
    print("="*80)
    print("CKM Cubic Suppression Law (Upgrade Log Sec 4)")
    print("="*80)

    # Load data
    df = pd.read_csv('ckm_geometric_features.csv')

    # Prepare features
    J_u_list = []
    J_d_list = []

    _, links = utils_v61.load_data()
    assignments = utils_v61.load_assignments()

    up_types = ["Up", "Charm", "Top"]
    down_types = ["Down", "Strange", "Bottom"]

    for u in up_types:
        topo = assignments[u]['topology'].split('{')[0]
        row = links[links['name'] == topo]
        if row.empty:
            row = links[links['name'].str.startswith(topo + "{")].iloc[0]
        else:
            row = row.iloc[0]
        jones = utils_v61.get_jones_at_root_of_unity(row['jones_polynomial'], n=5)
        J_u_list.append(abs(jones))

    for d in down_types:
        topo = assignments[d]['topology'].split('{')[0]
        row = links[links['name'] == topo]
        if row.empty:
            row = links[links['name'].str.startswith(topo + "{")].iloc[0]
        else:
            row = row.iloc[0]
        jones = utils_v61.get_jones_at_root_of_unity(row['jones_polynomial'], n=5)
        J_d_list.append(abs(jones))

    # Build feature matrices
    J_light_all = []
    J_heavy_all = []
    dV_all = []
    V_obs_all = []

    for i, J_u in enumerate(J_u_list):
        for j, J_d in enumerate(J_d_list):
            # Assume "light" is the quark with larger Jones (less complex)?
            # OR: light is up-type, heavy is down-type?
            # Let's try: light = min(J_u, J_d), heavy = max(J_u, J_d)
            J_light = min(J_u, J_d)
            J_heavy = max(J_u, J_d)

            J_light_all.append(J_light)
            J_heavy_all.append(J_heavy)
            dV_all.append(df.iloc[i*3 + j]['dV'])
            V_obs_all.append(df.iloc[i*3 + j]['obs'])

    J_light_all = np.array(J_light_all)
    J_heavy_all = np.array(J_heavy_all)
    dV_all = np.array(dV_all)
    V_obs_all = np.array(V_obs_all)

    # Fit Model 1: V = A * (J_l/J_h)^3 * exp(-k*dV)
    def objective_cubic(params):
        V_pred = model_cubic(params, J_light_all, J_heavy_all, dV_all)
        return -r2_score(V_obs_all, V_pred)

    print("\nFitting Model 1: V = A * (J_light/J_heavy)^3 * exp(-k*dV)")
    result1 = minimize(objective_cubic, [1.0, 0.1], method='Nelder-Mead', options={'maxiter': 5000})
    A_opt, k_opt = result1.x
    V_pred_1 = model_cubic([A_opt, k_opt], J_light_all, J_heavy_all, dV_all)
    r2_1 = r2_score(V_obs_all, V_pred_1)

    print(f"  A = {A_opt:.4f}")
    print(f"  k = {k_opt:.4f}")
    print(f"  R^2 = {r2_1:.4f}")

    # Fit Model 2: ln(V) = C + 3*ln(J_l/J_h) - k*dV
    def objective_log_cubic(params):
        V_pred = model_cubic_log(params, J_light_all, J_heavy_all, dV_all)
        return -r2_score(V_obs_all, V_pred)

    print("\nFitting Model 2: ln(V) = C + 3*ln(J_light/J_heavy) - k*dV")
    result2 = minimize(objective_log_cubic, [0.1, 0.0], method='Nelder-Mead', options={'maxiter': 5000})
    k_opt2, C_opt2 = result2.x
    V_pred_2 = model_cubic_log([k_opt2, C_opt2], J_light_all, J_heavy_all, dV_all)
    r2_2 = r2_score(V_obs_all, V_pred_2)

    print(f"  k = {k_opt2:.4f}")
    print(f"  C = {C_opt2:.4f}")
    print(f"  R^2 = {r2_2:.4f}")

    # Try alternative: J_light = J_up, J_heavy = J_down (generation ordering)
    print("\n" + "="*80)
    print("Alternative: J_light=J_up, J_heavy=J_down (generation semantics)")
    print("="*80)

    J_up_all = []
    J_down_all = []

    for i, J_u in enumerate(J_u_list):
        for j, J_d in enumerate(J_d_list):
            J_up_all.append(J_u)
            J_down_all.append(J_d)

    J_up_all = np.array(J_up_all)
    J_down_all = np.array(J_down_all)

    def objective_cubic_v2(params):
        V_pred = model_cubic(params, J_up_all, J_down_all, dV_all)
        return -r2_score(V_obs_all, V_pred)

    result3 = minimize(objective_cubic_v2, [1.0, 0.1], method='Nelder-Mead', options={'maxiter': 5000})
    A_opt3, k_opt3 = result3.x
    V_pred_3 = model_cubic([A_opt3, k_opt3], J_up_all, J_down_all, dV_all)
    r2_3 = r2_score(V_obs_all, V_pred_3)

    print(f"\nModel 3: V = A * (J_up/J_down)^3 * exp(-k*dV)")
    print(f"  A = {A_opt3:.4f}")
    print(f"  k = {k_opt3:.4f}")
    print(f"  R^2 = {r2_3:.4f}")

    # Compare
    print("\n" + "="*80)
    print("COMPARISON")
    print("="*80)
    print(f"  Model 1 (light/heavy min/max): R^2 = {r2_1:.4f}")
    print(f"  Model 2 (log-cubic):            R^2 = {r2_2:.4f}")
    print(f"  Model 3 (up/down semantics):    R^2 = {r2_3:.4f}")
    print(f"\nUpgrade Log claims R^2 = 0.6717 for this model.")
    print(f"Best achieved: {max(r2_1, r2_2, r2_3):.4f}")

    if max(r2_1, r2_2, r2_3) < 0.67:
        print("\n WARNING: Cannot reproduce claimed R^2 = 0.67")

if __name__ == "__main__":
    test_cubic_law()
