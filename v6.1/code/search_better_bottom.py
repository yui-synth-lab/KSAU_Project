"""
Search for Better Bottom Quark Topology
Goal: Find a link with volume ~12-13 but DIFFERENT Jones polynomial from Charm
to increase dlnJ(Charm-Bottom) and reduce V_cb prediction error
"""
import numpy as np
import pandas as pd
import utils_v61
from scipy.optimize import minimize
from sklearn.metrics import r2_score

def load_current_assignments():
    """Get current quark topologies"""
    assignments = utils_v61.load_assignments()
    _, links = utils_v61.load_data()

    quarks = {}
    for q in ["Up", "Charm", "Top", "Down", "Strange", "Bottom"]:
        topo = assignments[q]['topology'].split('{')[0]
        row = links[links['name'] == topo]
        if row.empty:
            row = links[links['name'].str.startswith(topo + "{")].iloc[0]
        else:
            row = row.iloc[0]

        jones = utils_v61.get_jones_at_root_of_unity(row['jones_polynomial'], n=5)
        quarks[q] = {
            'topology': topo,
            'volume': float(row['volume']),
            'jones_mag': abs(jones),
            'lnJ': np.log(max(1e-10, abs(jones))),
            'det': int(row['determinant']),
            'crossing': int(row['crossing_number'])
        }

    return quarks

def evaluate_ckm_r2(quarks, ckm_obs):
    """
    Evaluate R^2 for given quark assignment using best-fit coefficients
    """
    up_types = ["Up", "Charm", "Top"]
    down_types = ["Down", "Strange", "Bottom"]

    # Use best-fit params from regression (logit model)
    A, B, beta, gamma, C = -6.3436, 12.3988, -105.0351, 1.1253, 23.2475

    predictions = []
    observations = []

    for i, u in enumerate(up_types):
        for j, d in enumerate(down_types):
            V_u = quarks[u]['volume']
            V_d = quarks[d]['volume']
            lnJ_u = quarks[u]['lnJ']
            lnJ_d = quarks[d]['lnJ']

            dV = abs(V_u - V_d)
            dlnJ = abs(lnJ_u - lnJ_d)
            V_bar = (V_u + V_d) / 2.0

            logit_pred = C + A*dV + B*dlnJ + beta/V_bar + gamma*(dV*dlnJ)
            V_pred = 1.0 / (1.0 + np.exp(-logit_pred))

            predictions.append(V_pred)
            observations.append(ckm_obs[i][j])

    r2 = r2_score(observations, predictions)
    return r2, np.array(observations), np.array(predictions)

def search_bottom_candidates():
    """
    Search for better Bottom quark topology
    Requirements:
    - Volume: 12-13 (current Bottom is 12.28)
    - Generation 3 quark (should be complex)
    - Maximize dlnJ(Charm, Bottom) to reduce V_cb error
    """
    print("="*80)
    print("Searching for Better Bottom Quark Topology")
    print("="*80)

    # Load data
    _, links = utils_v61.load_data()
    current = load_current_assignments()
    consts = utils_v61.load_constants()
    ckm_obs = np.array(consts['ckm']['matrix'])

    # Current Bottom
    print(f"\nCurrent Bottom: {current['Bottom']['topology']}")
    print(f"  Volume: {current['Bottom']['volume']:.3f}")
    print(f"  lnJ: {current['Bottom']['lnJ']:.3f}")
    print(f"  Det: {current['Bottom']['det']}")

    # Current Charm (reference)
    print(f"\nCharm (reference): {current['Charm']['topology']}")
    print(f"  Volume: {current['Charm']['volume']:.3f}")
    print(f"  lnJ: {current['Charm']['lnJ']:.3f}")

    current_dlnJ_cb = abs(current['Charm']['lnJ'] - current['Bottom']['lnJ'])
    print(f"\nCurrent dlnJ(Charm, Bottom): {current_dlnJ_cb:.3f}")

    # Current R^2
    r2_current, _, _ = evaluate_ckm_r2(current, ckm_obs)
    print(f"Current R^2: {r2_current:.4f}")

    # Search criteria
    # - Volume: 11.5 - 13.5 (allow wider range)
    # - Determinant: prefer Det > 50 (generation 3 complexity)
    # - Crossing number: >= 9 (gen 3)
    # - Maximize |lnJ(new) - lnJ(Charm)|

    print("\n" + "="*80)
    print("Searching LinkInfo database...")
    print("="*80)

    candidates = []

    for _, row in links.iterrows():
        try:
            vol = float(row['volume'])
            det = int(row['determinant'])
            crossing = int(row['crossing_number'])

            # Filter
            if not (11.5 <= vol <= 13.5):
                continue
            if det < 50:
                continue
            if crossing < 9:
                continue

            # Compute Jones
            jones = utils_v61.get_jones_at_root_of_unity(row['jones_polynomial'], n=5)
            lnJ = np.log(max(1e-10, abs(jones)))

            # Distance from Charm
            dlnJ_charm = abs(lnJ - current['Charm']['lnJ'])

            # Test this candidate
            test_quarks = current.copy()
            test_quarks['Bottom'] = {
                'topology': row['name'],
                'volume': vol,
                'jones_mag': abs(jones),
                'lnJ': lnJ,
                'det': det,
                'crossing': crossing
            }

            r2_test, _, _ = evaluate_ckm_r2(test_quarks, ckm_obs)

            candidates.append({
                'name': row['name'],
                'volume': vol,
                'lnJ': lnJ,
                'dlnJ_charm': dlnJ_charm,
                'det': det,
                'crossing': crossing,
                'r2': r2_test,
                'improvement': r2_test - r2_current
            })

        except:
            continue

    # Sort by R^2 improvement
    candidates_df = pd.DataFrame(candidates)
    candidates_df = candidates_df.sort_values('r2', ascending=False)

    print(f"\nFound {len(candidates_df)} candidates")
    print("\nTop 20 candidates by R^2:")
    print("="*120)
    print(f"{'Topology':<15} | {'Volume':<8} | {'lnJ':<8} | {'dlnJ(C-B)':<10} | {'Det':<5} | {'Cross':<6} | {'R^2':<8} | {'Improv'}")
    print("="*120)

    for _, cand in candidates_df.head(20).iterrows():
        print(f"{cand['name']:<15} | {cand['volume']:<8.3f} | {cand['lnJ']:<8.3f} | "
              f"{cand['dlnJ_charm']:<10.3f} | {cand['det']:<5.0f} | {cand['crossing']:<6.0f} | "
              f"{cand['r2']:<8.4f} | {cand['improvement']:>+.4f}")

    # Best candidate
    best = candidates_df.iloc[0]
    print(f"\n{'='*80}")
    print(f"BEST CANDIDATE: {best['name']}")
    print(f"  Volume: {best['volume']:.3f} (current: {current['Bottom']['volume']:.3f})")
    print(f"  lnJ: {best['lnJ']:.3f} (current: {current['Bottom']['lnJ']:.3f})")
    print(f"  dlnJ(Charm-Bottom): {best['dlnJ_charm']:.3f} (current: {current_dlnJ_cb:.3f})")
    print(f"  R^2: {best['r2']:.4f} (current: {r2_current:.4f})")
    print(f"  Improvement: {best['improvement']:+.4f}")
    print(f"={'='*80}")

    # Save results
    candidates_df.head(50).to_csv('bottom_candidates.csv', index=False)
    print("\nSaved top 50 candidates to bottom_candidates.csv")

    return candidates_df

if __name__ == "__main__":
    search_bottom_candidates()
