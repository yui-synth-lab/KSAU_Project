"""
Constrained Quark Topology Optimization
CRITICAL CONSTRAINT: Volume ordering MUST match mass hierarchy
  Up < Down < Strange < Charm < Bottom < Top
"""
import numpy as np
import pandas as pd
import utils_v61
from sklearn.metrics import r2_score
import warnings
warnings.filterwarnings('ignore')

def evaluate_assignment_constrained(up_rows, down_rows, ckm_obs):
    """
    Evaluate R^2 with volume ordering constraint check
    Returns -999 if constraint violated
    """
    # Extract volumes
    volumes = {}
    for i, q in enumerate(['Up', 'Charm', 'Top']):
        volumes[q] = float(up_rows[i]['volume'])
    for i, q in enumerate(['Down', 'Strange', 'Bottom']):
        volumes[q] = float(down_rows[i]['volume'])

    # Check mass hierarchy constraint
    # Expected: Up < Down < Strange < Charm < Bottom < Top
    if not (volumes['Up'] < volumes['Down'] < volumes['Strange'] <
            volumes['Charm'] < volumes['Bottom'] < volumes['Top']):
        return -999  # Constraint violated

    # If constraint satisfied, evaluate CKM R^2
    A, B, beta, gamma, C = -6.3436, 12.3988, -105.0351, 1.1253, 23.2475

    predictions = []
    observations = []

    for i, u_row in enumerate(up_rows):
        for j, d_row in enumerate(down_rows):
            V_u = float(u_row['volume'])
            V_d = float(d_row['volume'])

            jones_u = utils_v61.get_jones_at_root_of_unity(u_row['jones_polynomial'], n=5)
            jones_d = utils_v61.get_jones_at_root_of_unity(d_row['jones_polynomial'], n=5)

            lnJ_u = np.log(max(1e-10, abs(jones_u)))
            lnJ_d = np.log(max(1e-10, abs(jones_d)))

            dV = abs(V_u - V_d)
            dlnJ = abs(lnJ_u - lnJ_d)
            V_bar = (V_u + V_d) / 2.0

            logit_pred = C + A*dV + B*dlnJ + beta/V_bar + gamma*(dV*dlnJ)
            V_pred = 1.0 / (1.0 + np.exp(-logit_pred))

            predictions.append(V_pred)
            observations.append(ckm_obs[i][j])

    try:
        r2 = r2_score(observations, predictions)
    except:
        r2 = -999

    return r2

def optimize_constrained():
    """
    Search for best assignment respecting mass hierarchy
    """
    print("="*80)
    print("Constrained Quark Topology Optimization")
    print("Constraint: Volume ordering = Mass hierarchy")
    print("="*80)

    # Load data
    _, links = utils_v61.load_data()
    consts = utils_v61.load_constants()
    ckm_obs = np.array(consts['ckm']['matrix'])

    print("\nRequired ordering: Up < Down < Strange < Charm < Bottom < Top")
    print()

    # Define stricter constraints to ensure ordering
    # Up: lightest (V < 6)
    # Down: V in [6, 7.5]
    # Strange: V in [7.5, 10]  # MUST be < Charm
    # Charm: V in [10, 12]     # MUST be > Strange
    # Bottom: V in [12, 14.5]  # MUST be < Top
    # Top: heaviest (V > 14.5)

    gen1_up = links[
        (links['volume'] >= 5) & (links['volume'] < 6) &
        (links['crossing_number'] <= 10) &
        (links['determinant'] >= 10)
    ].copy()

    gen1_down = links[
        (links['volume'] >= 6) & (links['volume'] < 7.5) &
        (links['crossing_number'] <= 10) &
        (links['determinant'] >= 10)
    ].copy()

    gen2_down_strange = links[
        (links['volume'] >= 7.5) & (links['volume'] < 10) &  # Upper bound to keep < Charm
        (links['crossing_number'] >= 8) &
        (links['determinant'] >= 20)
    ].copy()

    gen2_up_charm = links[
        (links['volume'] >= 10) & (links['volume'] < 12) &  # Lower bound to keep > Strange
        (links['crossing_number'] >= 8) &
        (links['determinant'] >= 30)
    ].copy()

    gen3_down_bottom = links[
        (links['volume'] >= 12) & (links['volume'] < 14.5) &  # Upper bound to keep < Top
        (links['crossing_number'] >= 9) &
        (links['determinant'] >= 50)
    ].copy()

    gen3_up_top = links[
        (links['volume'] >= 14.5) & (links['volume'] <= 17) &  # Lower bound to keep > Bottom
        (links['crossing_number'] >= 9) &
        (links['determinant'] >= 80)
    ].copy()

    print(f"Candidate pools:")
    print(f"  Up (V<6):          {len(gen1_up)}")
    print(f"  Down (6-7.5):      {len(gen1_down)}")
    print(f"  Strange (7.5-10):  {len(gen2_down_strange)}")
    print(f"  Charm (10-12):     {len(gen2_up_charm)}")
    print(f"  Bottom (12-14.5):  {len(gen3_down_bottom)}")
    print(f"  Top (>14.5):       {len(gen3_up_top)}")

    if min(len(gen1_up), len(gen1_down), len(gen2_down_strange),
           len(gen2_up_charm), len(gen3_down_bottom), len(gen3_up_top)) == 0:
        print("\n  ERROR: One or more pools empty - constraints too strict")
        return None, 0

    total = (len(gen1_up) * len(gen2_up_charm) * len(gen3_up_top) *
             len(gen1_down) * len(gen2_down_strange) * len(gen3_down_bottom))
    print(f"\nTotal combinations: {total:,}")

    n_samples = min(200000, total)
    print(f"Testing {n_samples:,} random combinations...")

    best_r2 = -999
    best_assignment = None

    np.random.seed(42)

    for trial in range(n_samples):
        try:
            up1 = gen1_up.sample(1).iloc[0]
            up2 = gen2_up_charm.sample(1).iloc[0]
            up3 = gen3_up_top.sample(1).iloc[0]
            down1 = gen1_down.sample(1).iloc[0]
            down2 = gen2_down_strange.sample(1).iloc[0]
            down3 = gen3_down_bottom.sample(1).iloc[0]

            up_rows = [up1, up2, up3]
            down_rows = [down1, down2, down3]

            r2 = evaluate_assignment_constrained(up_rows, down_rows, ckm_obs)

            if r2 > best_r2:
                best_r2 = r2
                best_assignment = {
                    'Up': up1, 'Charm': up2, 'Top': up3,
                    'Down': down1, 'Strange': down2, 'Bottom': down3
                }

                if best_r2 > 0.70:
                    print(f"\n  Trial {trial+1}: R^2 = {r2:.4f} (NEW BEST)")
                    for q in ['Up', 'Charm', 'Top', 'Down', 'Strange', 'Bottom']:
                        row = best_assignment[q]
                        print(f"    {q:<8}: {row['name']:<15} (V={row['volume']:.2f})")

        except Exception as e:
            continue

        if (trial + 1) % 20000 == 0:
            print(f"  Progress: {trial+1:,}/{n_samples:,} | Best R^2: {best_r2:.4f}")

    print("\n" + "="*80)
    print(f"OPTIMIZATION COMPLETE")
    print(f"Best R^2: {best_r2:.4f}")
    print("="*80)

    if best_assignment:
        print("\nBest 6-Quark Assignment (Mass-Hierarchy Constrained):")

        # Check final ordering
        volumes = {q: best_assignment[q]['volume'] for q in best_assignment.keys()}
        vol_order = [q for q, v in sorted(volumes.items(), key=lambda x: x[1])]

        print(f"\nVolume ordering: {' < '.join(vol_order)}")

        for q in ['Up', 'Charm', 'Top', 'Down', 'Strange', 'Bottom']:
            row = best_assignment[q]
            jones = utils_v61.get_jones_at_root_of_unity(row['jones_polynomial'], n=5)
            print(f"  {q:<8}: {row['name']:<20} | V={row['volume']:<7.3f} | Det={row['determinant']:<4} | lnJ={np.log(abs(jones)):.3f}")

        # Save
        with open('best_quark_assignment_constrained.txt', 'w') as f:
            f.write(f"Best R^2: {best_r2:.4f}\n\n")
            for q in ['Up', 'Charm', 'Top', 'Down', 'Strange', 'Bottom']:
                row = best_assignment[q]
                f.write(f"{q}: {row['name']} (V={row['volume']:.3f}, Det={row['determinant']})\n")

        print("\nSaved to best_quark_assignment_constrained.txt")

    return best_assignment, best_r2

if __name__ == "__main__":
    optimize_constrained()
