"""
Global Quark Topology Optimization
Search for best 6-quark assignment to maximize CKM R^2
Uses constrained search with generation and volume ordering
"""
import numpy as np
import pandas as pd
import utils_v61
from sklearn.metrics import r2_score
from itertools import combinations
import warnings
warnings.filterwarnings('ignore')

def evaluate_assignment(up_rows, down_rows, ckm_obs):
    """
    Evaluate R^2 for a 6-quark assignment
    up_rows: [Up, Charm, Top] link rows
    down_rows: [Down, Strange, Bottom] link rows
    """
    # Best-fit coefficients (from regression)
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

def optimize_quarks():
    """
    Constrained search for optimal quark topologies
    """
    print("="*80)
    print("Global Quark Topology Optimization (Constrained Search)")
    print("="*80)

    # Load data
    _, links = utils_v61.load_data()
    consts = utils_v61.load_constants()
    ckm_obs = np.array(consts['ckm']['matrix'])

    # Define search space constraints
    # Generation 1 (light): Volume 5-8, Crossing <= 10
    # Generation 2 (medium): Volume 9-12, Crossing >= 8
    # Generation 3 (heavy): Volume 12-16, Crossing >= 9

    print("\nFiltering candidates by generation constraints...")

    gen1_up = links[
        (links['volume'] >= 5) & (links['volume'] <= 8) &
        (links['crossing_number'] <= 10) &
        (links['determinant'] >= 10)
    ].copy()

    gen1_down = links[
        (links['volume'] >= 6) & (links['volume'] <= 9) &
        (links['crossing_number'] <= 10) &
        (links['determinant'] >= 10)
    ].copy()

    gen2_up = links[
        (links['volume'] >= 10) & (links['volume'] <= 13) &
        (links['crossing_number'] >= 8) &
        (links['determinant'] >= 30)
    ].copy()

    gen2_down = links[
        (links['volume'] >= 8.5) & (links['volume'] <= 11) &
        (links['crossing_number'] >= 8) &
        (links['determinant'] >= 20)
    ].copy()

    gen3_up = links[
        (links['volume'] >= 14) & (links['volume'] <= 17) &
        (links['crossing_number'] >= 9) &
        (links['determinant'] >= 80)
    ].copy()

    gen3_down = links[
        (links['volume'] >= 11.5) & (links['volume'] <= 14) &
        (links['crossing_number'] >= 9) &
        (links['determinant'] >= 50)
    ].copy()

    print(f"  Gen1 Up:   {len(gen1_up)} candidates")
    print(f"  Gen1 Down: {len(gen1_down)} candidates")
    print(f"  Gen2 Up:   {len(gen2_up)} candidates")
    print(f"  Gen2 Down: {len(gen2_down)} candidates")
    print(f"  Gen3 Up:   {len(gen3_up)} candidates")
    print(f"  Gen3 Down: {len(gen3_down)} candidates")

    total_combinations = len(gen1_up) * len(gen2_up) * len(gen3_up) * len(gen1_down) * len(gen2_down) * len(gen3_down)
    print(f"\nTotal possible combinations: {total_combinations:,}")

    # Sample-based search (test random combinations)
    n_samples = min(100000, total_combinations)
    print(f"Testing {n_samples:,} random combinations...")

    best_r2 = -999
    best_assignment = None

    np.random.seed(42)

    for trial in range(n_samples):
        try:
            # Sample one from each generation
            up1 = gen1_up.sample(1).iloc[0]
            up2 = gen2_up.sample(1).iloc[0]
            up3 = gen3_up.sample(1).iloc[0]
            down1 = gen1_down.sample(1).iloc[0]
            down2 = gen2_down.sample(1).iloc[0]
            down3 = gen3_down.sample(1).iloc[0]

            up_rows = [up1, up2, up3]
            down_rows = [down1, down2, down3]

            r2 = evaluate_assignment(up_rows, down_rows, ckm_obs)

            if r2 > best_r2:
                best_r2 = r2
                best_assignment = {
                    'Up': up1, 'Charm': up2, 'Top': up3,
                    'Down': down1, 'Strange': down2, 'Bottom': down3
                }

                # Print progress
                if best_r2 > 0.50:
                    print(f"\n  Trial {trial+1}: R^2 = {r2:.4f} (NEW BEST)")
                    for q in ['Up', 'Charm', 'Top', 'Down', 'Strange', 'Bottom']:
                        row = best_assignment[q]
                        print(f"    {q:<8}: {row['name']:<15} (V={row['volume']:.2f}, Det={row['determinant']})")

        except Exception as e:
            continue

        if (trial + 1) % 10000 == 0:
            print(f"  Progress: {trial+1:,}/{n_samples:,} | Best R^2: {best_r2:.4f}")

    print("\n" + "="*80)
    print(f"OPTIMIZATION COMPLETE")
    print(f"Best R^2: {best_r2:.4f}")
    print("="*80)

    if best_assignment:
        print("\nBest 6-Quark Assignment:")
        for q in ['Up', 'Charm', 'Top', 'Down', 'Strange', 'Bottom']:
            row = best_assignment[q]
            jones = utils_v61.get_jones_at_root_of_unity(row['jones_polynomial'], n=5)
            print(f"  {q:<8}: {row['name']:<20} | V={row['volume']:<7.3f} | Det={row['determinant']:<4} | lnJ={np.log(abs(jones)):.3f}")

        # Save to file
        with open('best_quark_assignment.txt', 'w') as f:
            f.write(f"Best R^2: {best_r2:.4f}\n\n")
            for q in ['Up', 'Charm', 'Top', 'Down', 'Strange', 'Bottom']:
                row = best_assignment[q]
                f.write(f"{q}: {row['name']} (V={row['volume']:.3f}, Det={row['determinant']})\n")

        print("\nSaved to best_quark_assignment.txt")

    return best_assignment, best_r2

if __name__ == "__main__":
    optimize_quarks()
