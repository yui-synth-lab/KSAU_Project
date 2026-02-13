"""
Validate the new quark topology assignment found by optimization
"""
import numpy as np
import pandas as pd
import utils_v61
from sklearn.metrics import r2_score

def validate_assignment():
    print("="*80)
    print("Validating New Quark Topology Assignment")
    print("="*80)

    # New assignment from optimization
    new_assignment = {
        'Up': 'L8n1{0}',
        'Charm': 'L11a358{0}',
        'Top': 'L11n409{1,0}',
        'Down': 'L7a3{1}',
        'Strange': 'L9a49{1,0}',
        'Bottom': 'L11n113{1}'
    }

    # Load data
    _, links = utils_v61.load_data()
    consts = utils_v61.load_constants()
    ckm_obs = np.array(consts['ckm']['matrix'])

    # Best-fit coefficients
    A, B, beta, gamma, C = -6.3436, 12.3988, -105.0351, 1.1253, 23.2475

    up_types = ["Up", "Charm", "Top"]
    down_types = ["Down", "Strange", "Bottom"]

    predictions = []
    observations = []
    details = []

    print("\nNew Topology Assignment:")
    print("-" * 80)
    for q in ['Up', 'Charm', 'Top', 'Down', 'Strange', 'Bottom']:
        topo = new_assignment[q].split('{')[0]
        row = links[links['name'] == topo]
        if row.empty:
            row = links[links['name'].str.startswith(topo + "{")].iloc[0]
        else:
            row = row.iloc[0]
        print(f"  {q:<8}: {new_assignment[q]:<20} | V={float(row['volume']):<7.3f} | Det={int(row['determinant']):<4}")

    print("\n" + "="*80)
    print("CKM Predictions with New Assignment")
    print("="*80)

    for i, u in enumerate(up_types):
        for j, d in enumerate(down_types):
            # Get topologies
            u_topo = new_assignment[u].split('{')[0]
            d_topo = new_assignment[d].split('{')[0]

            u_row = links[links['name'] == u_topo]
            if u_row.empty:
                u_row = links[links['name'].str.startswith(u_topo + "{")].iloc[0]
            else:
                u_row = u_row.iloc[0]

            d_row = links[links['name'] == d_topo]
            if d_row.empty:
                d_row = links[links['name'].str.startswith(d_topo + "{")].iloc[0]
            else:
                d_row = d_row.iloc[0]

            # Compute features
            V_u = float(u_row['volume'])
            V_d = float(d_row['volume'])

            jones_u = utils_v61.get_jones_at_root_of_unity(u_row['jones_polynomial'], n=5)
            jones_d = utils_v61.get_jones_at_root_of_unity(d_row['jones_polynomial'], n=5)

            lnJ_u = np.log(max(1e-10, abs(jones_u)))
            lnJ_d = np.log(max(1e-10, abs(jones_d)))

            dV = abs(V_u - V_d)
            dlnJ = abs(lnJ_u - lnJ_d)
            V_bar = (V_u + V_d) / 2.0

            # Predict
            logit_pred = C + A*dV + B*dlnJ + beta/V_bar + gamma*(dV*dlnJ)
            V_pred = 1.0 / (1.0 + np.exp(-logit_pred))

            obs = ckm_obs[i][j]
            predictions.append(V_pred)
            observations.append(obs)

            details.append({
                'transition': f"{u}-{d}",
                'obs': obs,
                'pred': V_pred,
                'error_pct': abs(obs - V_pred) / obs * 100,
                'dV': dV,
                'dlnJ': dlnJ
            })

    # Calculate R^2
    r2 = r2_score(observations, predictions)

    # Print table
    print(f"\n{'Transition':<15} | {'Observed':<10} | {'Predicted':<10} | {'Error %':<10} | {'dV':<8} | {'dlnJ'}")
    print("-" * 90)
    for d in details:
        print(f"{d['transition']:<15} | {d['obs']:<10.4f} | {d['pred']:<10.4f} | {d['error_pct']:<10.2f} | {d['dV']:<8.3f} | {d['dlnJ']:.3f}")

    print("-" * 90)
    print(f"R^2: {r2:.4f}")
    print(f"MAE: {np.mean([d['error_pct'] for d in details]):.2f}%")

    # Compare with old assignment
    print("\n" + "="*80)
    print("COMPARISON")
    print("="*80)
    print(f"Old Assignment (v6.0 SSoT): R^2 = 0.4408")
    print(f"New Assignment (optimized):  R^2 = {r2:.4f}")
    print(f"Improvement: {(r2 - 0.4408):.4f} ({(r2 - 0.4408)/0.4408 * 100:+.1f}%)")

    if r2 > 0.70:
        print("\n SUCCESS: R^2 > 0.70 TARGET ACHIEVED!")
    else:
        print(f"\n WARNING: R^2 = {r2:.4f} < 0.70 target")

    # Save
    df_details = pd.DataFrame(details)
    df_details.to_csv('ckm_new_assignment_validation.csv', index=False)
    print("\nSaved detailed results to ckm_new_assignment_validation.csv")

if __name__ == "__main__":
    validate_assignment()
