"""
Improved PMNS Neutrino Candidate Search
Uses multiple topological metrics beyond just Unknotting Efficiency
"""
import numpy as np
import pandas as pd
import utils_v61

def compute_metrics(row):
    """
    Compute multiple topological metrics for neutrino candidate ranking
    """
    vol = float(row['volume'])

    # Unknotting number
    u_num = float(row['unknotting_number']) if pd.notna(row['unknotting_number']) else 1.0

    # Jones polynomial magnitude at root of unity
    jones = utils_v61.get_jones_at_root_of_unity(row['jones_polynomial'], n=5)
    j_mag = abs(jones)

    # Determinant
    det = int(row['determinant'])

    # Crossing number
    cross = int(row['crossing_number'])

    # Three-genus (if available)
    try:
        genus = int(row['three_genus'])
    except:
        genus = 0

    # Metrics
    # 1. Original: Unknotting Efficiency
    eff_unknot = vol / u_num if u_num > 0 else vol

    # 2. Surgery Complexity (Volume / Genus)
    eff_genus = vol / genus if genus > 0 else 0

    # 3. Jones-Volume Resonance
    eff_jones = vol * j_mag

    # 4. Normalized Complexity (Volume / Crossing Number)
    eff_crossing = vol / cross if cross > 0 else 0

    # 5. Hybrid: Volume * Jones / Determinant
    eff_hybrid = (vol * j_mag) / det if det > 0 else 0

    return {
        'name': row['name'],
        'vol': vol,
        'u_num': u_num,
        'genus': genus,
        'det': det,
        'cross': cross,
        'j_mag': j_mag,
        'eff_unknot': eff_unknot,
        'eff_genus': eff_genus,
        'eff_jones': eff_jones,
        'eff_crossing': eff_crossing,
        'eff_hybrid': eff_hybrid
    }

def search_triplet_multi_metric():
    """
    Search for best neutrino triplet using multiple metrics
    """
    print("="*80)
    print("PMNS Improved Neutrino Candidate Search (Multi-Metric)")
    print("="*80)

    # Load data
    knots, _ = utils_v61.load_data()
    consts = utils_v61.load_constants()

    # PMNS target angles
    pmns_data = consts['neutrinos']['pmns_angles_deg']
    theta12_obs = pmns_data['theta12']  # 33.4
    theta23_obs = pmns_data['theta23']  # 49.0
    theta13_obs = pmns_data['theta13']  # 8.6

    targets = sorted([theta12_obs, theta23_obs, theta13_obs])

    # Filter candidates (expand search range)
    # Allow crossing up to 10 (include more candidates)
    candidates = knots[knots['crossing_number'] <= 10].copy()

    print(f"\nTotal candidates (crossing <= 10): {len(candidates)}")

    # Compute all metrics
    metrics_list = []
    for _, row in candidates.iterrows():
        try:
            m = compute_metrics(row)
            metrics_list.append(m)
        except:
            continue

    df = pd.DataFrame(metrics_list)

    print(f"Candidates with valid metrics: {len(df)}")

    # Test each metric
    metric_names = ['eff_unknot', 'eff_genus', 'eff_jones', 'eff_crossing', 'eff_hybrid']

    results = {}

    for metric in metric_names:
        print(f"\n{'='*80}")
        print(f"Testing Metric: {metric}")
        print(f"{'='*80}")

        # Filter out zeros/invalids for this metric
        df_valid = df[df[metric] > 0].copy()

        if len(df_valid) < 3:
            print(f"  Insufficient candidates ({len(df_valid)}) - SKIP")
            continue

        # Search for best triplet
        best_score = float('inf')
        best_triplet = None

        # Sample search (top 50 candidates to reduce search space)
        search_pool = df_valid.nlargest(50, metric).to_dict('records')

        for i in range(len(search_pool)):
            for j in range(i+1, len(search_pool)):
                for k in range(j+1, len(search_pool)):
                    n1, n2, n3 = search_pool[i], search_pool[j], search_pool[k]

                    # Pairwise distances
                    d12 = abs(n1[metric] - n2[metric])
                    d23 = abs(n2[metric] - n3[metric])
                    d13 = abs(n1[metric] - n3[metric])

                    dists = sorted([d12, d23, d13])

                    # Linear scaling fit
                    x = np.array(dists)
                    y = np.array(targets)

                    if np.sum(x**2) == 0:
                        continue

                    slope = np.sum(x*y) / np.sum(x**2)
                    preds = slope * x
                    mse = np.mean((y - preds)**2)

                    if mse < best_score:
                        best_score = mse
                        best_triplet = (n1, n2, n3, slope, preds, dists)

        if best_triplet:
            n1, n2, n3, slope, preds, dists = best_triplet

            print(f"  Best Triplet:")
            print(f"    nu1: {n1['name']:<10} ({metric}={n1[metric]:.4f})")
            print(f"    nu2: {n2['name']:<10} ({metric}={n2[metric]:.4f})")
            print(f"    nu3: {n3['name']:<10} ({metric}={n3[metric]:.4f})")
            print(f"  Scaling: {slope:.2f} deg/unit")
            print(f"  MSE: {best_score:.2f} deg^2")

            print(f"\n  Angle Predictions:")
            for d, p, t in zip(dists, preds, targets):
                print(f"    Distance {d:.4f} → Pred {p:.2f}° (Target {t}°)")

            results[metric] = {
                'triplet': (n1['name'], n2['name'], n3['name']),
                'mse': best_score,
                'slope': slope
            }

    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY: Best Triplet per Metric")
    print(f"{'='*80}")
    print(f"{'Metric':<20} | {'Triplet':<30} | {'MSE (deg^2)':<12}")
    print("-"*80)

    for metric, res in results.items():
        triplet_str = f"{res['triplet'][0]}, {res['triplet'][1]}, {res['triplet'][2]}"
        print(f"{metric:<20} | {triplet_str:<30} | {res['mse']:<12.2f}")

    # Best overall
    if results:
        best_metric = min(results.keys(), key=lambda m: results[m]['mse'])
        best_res = results[best_metric]

        print(f"\n{'='*80}")
        print(f"BEST METRIC: {best_metric}")
        print(f"  Triplet: {best_res['triplet']}")
        print(f"  MSE: {best_res['mse']:.2f} deg^2")
        print(f"{'='*80}")

        # Save
        with open('pmns_best_triplet_multi_metric.txt', 'w') as f:
            f.write(f"Best Metric: {best_metric}\n")
            f.write(f"MSE: {best_res['mse']:.2f} deg^2\n")
            f.write(f"Triplet: {best_res['triplet']}\n")

        print("\nSaved to pmns_best_triplet_multi_metric.txt")

    return results

if __name__ == "__main__":
    search_triplet_multi_metric()
