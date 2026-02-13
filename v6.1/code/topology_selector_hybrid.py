"""
Hybrid Topology Selector (Deterministic + Small Optimization)

Algorithm:
1. For each quark, select top-N candidates by volume proximity to mass-derived target
2. Exhaustively evaluate all N^6 combinations
3. Return the one with highest CKM R^2 that satisfies mass hierarchy

This is FULLY DETERMINISTIC and REPRODUCIBLE (no random seed needed)
"""
import numpy as np
import pandas as pd
import utils_v61
from sklearn.metrics import r2_score
from itertools import product

def compute_target_volumes(observed_masses):
    """Same as deterministic selector"""
    ln_m_up = np.log(observed_masses['Up'])
    ln_m_top = np.log(observed_masses['Top'])

    V_up_target = 5.5
    V_top_target = 16.5

    a = (V_top_target - V_up_target) / (ln_m_top - ln_m_up)
    b = V_up_target - a * ln_m_up

    return {
        'Up': a * np.log(observed_masses['Up']) + b,
        'Down': a * np.log(observed_masses['Down']) + b,
        'Strange': a * np.log(observed_masses['Strange']) + b,
        'Charm': a * np.log(observed_masses['Charm']) + b,
        'Bottom': a * np.log(observed_masses['Bottom']) + b,
        'Top': a * np.log(observed_masses['Top']) + b
    }

def select_top_n_candidates(quark_name, target_volume, links, generation, n=5):
    """Select top N candidates by volume proximity"""
    gen_constraints = {
        1: {'det_min': 10, 'det_max': 30, 'cross_min': 6, 'cross_max': 10},
        2: {'det_min': 30, 'det_max': 70, 'cross_min': 8, 'cross_max': 11},
        3: {'det_min': 60, 'det_max': 150, 'cross_min': 9, 'cross_max': 12}
    }

    const = gen_constraints[generation]

    pool = links[
        (links['determinant'] >= const['det_min']) &
        (links['determinant'] <= const['det_max']) &
        (links['crossing_number'] >= const['cross_min']) &
        (links['crossing_number'] <= const['cross_max'])
    ].copy()

    pool['volume_deviation'] = np.abs(pool['volume'] - target_volume)
    top_n = pool.nsmallest(n, 'volume_deviation')

    return list(top_n.to_dict('records'))

def evaluate_ckm_for_assignment(assignment, ckm_obs):
    """Evaluate CKM R^2 for a 6-quark assignment"""
    A, B, beta, gamma, C = -6.3436, 12.3988, -105.0351, 1.1253, 23.2475

    up_types = ["Up", "Charm", "Top"]
    down_types = ["Down", "Strange", "Bottom"]

    predictions = []
    observations = []

    for i, u in enumerate(up_types):
        for j, d in enumerate(down_types):
            u_row = assignment[u]
            d_row = assignment[d]

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

def hybrid_topology_selection(top_n=5):
    """
    Main hybrid algorithm
    """
    print("="*80)
    print("Hybrid Topology Selector (Deterministic)")
    print(f"Strategy: Top-{top_n} volume candidates per quark, exhaustive CKM evaluation")
    print("="*80)

    # Load data
    _, links = utils_v61.load_data()
    consts = utils_v61.load_constants()

    observed_masses = {q: consts['quarks'][q]['observed_mass']
                      for q in ['Up', 'Down', 'Charm', 'Strange', 'Top', 'Bottom']}

    ckm_obs = np.array(consts['ckm']['matrix'])

    # Step 1: Target volumes
    print("\n[STEP 1] Computing target volumes...")
    target_volumes = compute_target_volumes(observed_masses)

    for q in ['Up', 'Down', 'Strange', 'Charm', 'Bottom', 'Top']:
        print(f"  {q:<8}: V_target = {target_volumes[q]:.3f}")

    # Step 2: Select top-N candidates per quark
    print(f"\n[STEP 2] Selecting top-{top_n} volume-matched candidates per quark...")

    quark_gen = {
        'Up': 1, 'Down': 1,
        'Charm': 2, 'Strange': 2,
        'Top': 3, 'Bottom': 3
    }

    candidates = {}
    for quark in ['Up', 'Down', 'Strange', 'Charm', 'Bottom', 'Top']:
        top_n_list = select_top_n_candidates(
            quark, target_volumes[quark], links, quark_gen[quark], n=top_n
        )
        candidates[quark] = top_n_list
        print(f"  {quark:<8}: {len(top_n_list)} candidates")

    # Step 3: Exhaustive evaluation
    total_combinations = top_n ** 6
    print(f"\n[STEP 3] Exhaustively evaluating {total_combinations:,} combinations...")

    best_r2 = -999
    best_assignment = None

    mass_order = ['Up', 'Down', 'Strange', 'Charm', 'Bottom', 'Top']

    evaluated = 0
    valid = 0

    for combo in product(candidates['Up'], candidates['Down'], candidates['Strange'],
                        candidates['Charm'], candidates['Bottom'], candidates['Top']):
        evaluated += 1

        assignment = {q: row for q, row in zip(mass_order, combo)}

        # Check mass hierarchy constraint
        volumes = {q: assignment[q]['volume'] for q in mass_order}
        vol_order = [q for q, v in sorted(volumes.items(), key=lambda x: x[1])]

        if vol_order != mass_order:
            continue  # Violates constraint

        # Check uniqueness
        topo_names = [assignment[q]['name'] for q in mass_order]
        if len(set(topo_names)) != 6:
            continue  # Duplicate topology

        valid += 1

        # Evaluate CKM R^2
        r2 = evaluate_ckm_for_assignment(assignment, ckm_obs)

        if r2 > best_r2:
            best_r2 = r2
            best_assignment = assignment

            if valid % 100 == 0 or r2 > 0.95:
                print(f"    Progress: {evaluated:,}/{total_combinations:,} | Valid: {valid} | Best R^2: {r2:.4f}")

    print(f"\n  Total evaluated: {evaluated:,}")
    print(f"  Valid (constraints satisfied): {valid}")
    print(f"  Best R^2: {best_r2:.4f}")

    # Step 4: Report result
    print("\n" + "="*80)
    print("HYBRID SELECTION COMPLETE (DETERMINISTIC)")
    print(f"R^2: {best_r2:.4f}")
    print("="*80)

    if best_assignment:
        print("\nFinal Topology Assignment:")
        for q in mass_order:
            row = best_assignment[q]
            print(f"  {q:<8}: {row['name']:<20} (V={row['volume']:.3f}, Det={row['determinant']})")

        # Save
        with open('topology_selection_hybrid.txt', 'w') as f:
            f.write("Hybrid Topology Selection Results (DETERMINISTIC)\n")
            f.write("="*60 + "\n")
            f.write(f"Top-N candidates per quark: {top_n}\n")
            f.write(f"Total combinations evaluated: {evaluated:,}\n")
            f.write(f"Valid combinations: {valid}\n")
            f.write(f"R^2: {best_r2:.4f}\n\n")
            f.write("Algorithm:\n")
            f.write("  1. Compute target volumes from mass-volume correlation\n")
            f.write(f"  2. Select top-{top_n} volume-matched candidates per quark\n")
            f.write(f"  3. Exhaustively evaluate all {top_n}^6 combinations\n")
            f.write("  4. Return best CKM R^2 satisfying mass hierarchy\n\n")
            f.write("Final Assignment:\n")
            for q in mass_order:
                row = best_assignment[q]
                f.write(f"{q}: {row['name']} (V={row['volume']:.3f}, Det={row['determinant']})\n")

        print("\nSaved to topology_selection_hybrid.txt")

    return best_assignment, best_r2

if __name__ == "__main__":
    # Test with N=10 (1,000,000 combinations)
    hybrid_topology_selection(top_n=10)
