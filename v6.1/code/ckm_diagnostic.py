"""
CKM Model Diagnostic Analysis
Identifies failure modes and computes geometric invariants for all transitions
"""
import numpy as np
import pandas as pd
import utils_v61

def analyze_ckm_geometry():
    print("="*80)
    print("CKM Geometric Diagnostic Analysis")
    print("="*80)

    # Load data
    _, links = utils_v61.load_data()
    assignments = utils_v61.load_assignments()
    consts = utils_v61.load_constants()

    ckm_obs = np.array(consts['ckm']['matrix'])
    up_types = ["Up", "Charm", "Top"]
    down_types = ["Down", "Strange", "Bottom"]

    # Collect all geometric features
    data = []

    for i, u in enumerate(up_types):
        for j, d in enumerate(down_types):
            # Get topologies
            u_topo = assignments[u]['topology'].split('{')[0]
            d_topo = assignments[d]['topology'].split('{')[0]

            # Get rows
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

            # Volume
            V_u = float(u_row['volume'])
            V_d = float(d_row['volume'])
            dV = abs(V_u - V_d)
            V_bar = (V_u + V_d) / 2.0

            # Jones polynomial
            jones_u = utils_v61.get_jones_at_root_of_unity(u_row['jones_polynomial'], n=5)
            jones_d = utils_v61.get_jones_at_root_of_unity(d_row['jones_polynomial'], n=5)
            J_u = abs(jones_u)
            J_d = abs(jones_d)
            lnJ_u = np.log(max(1e-10, J_u))
            lnJ_d = np.log(max(1e-10, J_d))
            dlnJ = abs(lnJ_u - lnJ_d)

            # Determinant
            det_u = int(u_row['determinant'])
            det_d = int(d_row['determinant'])

            # Crossing number
            cross_u = int(u_row['crossing_number'])
            cross_d = int(d_row['crossing_number'])

            obs = ckm_obs[i, j]

            data.append({
                'transition': f"{u}-{d}",
                'obs': obs,
                'is_diagonal': (i == j),
                'gen_gap': abs(i - j),
                'V_u': V_u,
                'V_d': V_d,
                'dV': dV,
                'V_bar': V_bar,
                'J_u': J_u,
                'J_d': J_d,
                'lnJ_u': lnJ_u,
                'lnJ_d': lnJ_d,
                'dlnJ': dlnJ,
                'det_u': det_u,
                'det_d': det_d,
                'cross_u': cross_u,
                'cross_d': cross_d
            })

    df = pd.DataFrame(data)

    # Print table
    print("\n" + "="*120)
    print(f"{'Transition':<12} | {'Obs':<8} | {'dV':<8} | {'dlnJ':<8} | {'V_bar':<8} | {'1/V_bar':<8} | {'dV*dlnJ':<10} | {'Type'}")
    print("="*120)

    for _, row in df.iterrows():
        transition_type = "DIAG" if row['is_diagonal'] else f"Gap{row['gen_gap']}"
        print(f"{row['transition']:<12} | {row['obs']:<8.4f} | {row['dV']:<8.3f} | {row['dlnJ']:<8.3f} | "
              f"{row['V_bar']:<8.3f} | {1/row['V_bar']:<8.4f} | {row['dV']*row['dlnJ']:<10.4f} | {transition_type}")

    print("="*120)

    # Correlation analysis
    print("\n" + "="*80)
    print("Correlation Analysis: obs vs geometric features")
    print("="*80)

    # Log-transform obs for better correlation
    df['ln_obs'] = np.log(df['obs'])
    df['logit_obs'] = np.log(df['obs'] / (1 - df['obs']))

    features = ['dV', 'dlnJ', 'V_bar', 'dV*dlnJ']
    df['dV*dlnJ'] = df['dV'] * df['dlnJ']
    df['1/V_bar'] = 1.0 / df['V_bar']

    for target in ['obs', 'ln_obs', 'logit_obs']:
        print(f"\nCorrelations with {target}:")
        for feat in ['dV', 'dlnJ', '1/V_bar', 'dV*dlnJ']:
            corr = df[feat].corr(df[target])
            print(f"  {feat:<12}: {corr:>7.4f}")

    # Identify problem transitions
    print("\n" + "="*80)
    print("Problem Transitions (high |obs|, high dV or high dlnJ)")
    print("="*80)

    # Diagonal should be high obs, low dV
    diag = df[df['is_diagonal']]
    print("\nDiagonal elements (should be ~1):")
    for _, row in diag.iterrows():
        print(f"  {row['transition']}: obs={row['obs']:.4f}, dV={row['dV']:.3f}, dlnJ={row['dlnJ']:.3f}")

    # Off-diagonal should be low obs
    off_diag = df[~df['is_diagonal']]
    print("\nOff-diagonal elements (should be small):")
    for _, row in off_diag.iterrows():
        print(f"  {row['transition']}: obs={row['obs']:.4f}, dV={row['dV']:.3f}, dlnJ={row['dlnJ']:.3f}")

    # Save for regression
    df.to_csv('ckm_geometric_features.csv', index=False)
    print("\nSaved geometric features to ckm_geometric_features.csv")

    return df

if __name__ == "__main__":
    analyze_ckm_geometry()
