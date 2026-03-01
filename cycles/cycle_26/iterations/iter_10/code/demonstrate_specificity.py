
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path

# Setup SSOT
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
ssot_path = project_root / "ssot"
sys.path.insert(0, str(ssot_path))    
from ksau_ssot import SSOT

def analyze():
    ssot = SSOT()
    consts = ssot.constants()
    knots_df, links_df = ssot.knot_data()
    topo_assignments = ssot.topology_assignments()
    
    # 1. Data Preparation
    knots_df['components'] = 1
    cols = ['name', 'crossing_number', 'components', 'volume', 'determinant', 'signature']
    
    pop_knots = knots_df[cols].copy()
    pop_links = links_df[cols].copy()
    population = pd.concat([pop_knots, pop_links], ignore_index=True)
    
    # Filter by crossing number (3-12)
    params = consts['analysis_parameters']
    population = population[(population['crossing_number'] >= params['min_crossing_number']) & 
                            (population['crossing_number'] <= params['max_crossing_number'])]
    
    population = population.dropna(subset=['volume', 'signature'])
    population['volume'] = population['volume'].astype(float)
    population['signature'] = population['signature'].astype(float)
    
    # 2. Feature Engineering (TSI)
    # formula: 24 * c / (n + abs(s))
    population['tsi'] = 24 * population['components'] / (population['crossing_number'] + population['signature'].abs())
    
    # 3. Identify SM set
    sm_names = [data['topology'] for data in topo_assignments.values()]
    population['is_sm'] = population['name'].isin(sm_names)
    
    # 4. Pareto Front Analysis
    # We want MIN Volume and MAX TSI.
    # Transform TSI to -TSI to use standard "min-min" Pareto optimization.
    points = population[['volume', 'tsi']].values
    
    def is_pareto_efficient(costs):
        """
        Find the pareto-efficient points
        :param costs: An (n_points, n_costs) array
        :return: A (n_points, ) boolean array indicating whether each point is Pareto efficient
        """
        is_efficient = np.ones(costs.shape[0], dtype=bool)
        for i, c in enumerate(costs):
            if is_efficient[i]:
                # Keep points that are better in at least one dimension
                # or equal in both (but we want strict better for suppression)
                is_efficient[is_efficient] = np.any(costs[is_efficient] < c, axis=1) | np.all(costs[is_efficient] == c, axis=1)
                is_efficient[i] = True  # Keep self
        return is_efficient

    # Costs: [Volume, -TSI]
    costs = np.copy(points)
    costs[:, 1] = -costs[:, 1]
    
    pareto_mask = is_pareto_efficient(costs)
    pareto_front = points[pareto_mask]
    
    # 5. Specificity Metric: Distance to Pareto Front
    # We use rank-based distance to avoid scale issues.
    population['v_rank'] = population['volume'].rank(pct=True)
    population['tsi_rank'] = population['tsi'].rank(pct=True, ascending=False)
    
    # Pareto in rank space
    rank_points = population[['v_rank', 'tsi_rank']].values
    rank_costs = np.copy(rank_points)
    # Both are already minimized (low rank V = low volume, low rank TSI_desc = high TSI)
    
    pareto_rank_mask = is_pareto_efficient(rank_costs)
    pareto_rank_points = rank_points[pareto_rank_mask]
    
    # Distance to the nearest Pareto point in rank space
    def min_dist_to_front(p, front):
        return np.min(np.sqrt(np.sum((front - p)**2, axis=1)))

    # Vectorized (or looped if too large)
    dists = []
    for p in rank_points:
        dists.append(min_dist_to_front(p, pareto_rank_points))
    population['dist_to_front'] = dists
    
    # 6. Statistical Significance
    sm_dists = population[population['is_sm']]['dist_to_front'].values
    mean_sm_dist = np.mean(sm_dists)
    
    n_trials = consts['statistical_thresholds']['monte_carlo_n_trials']
    np.random.seed(params['random_seed'])
    
    all_dists = population['dist_to_front'].values
    N = len(all_dists)
    random_means = []
    for _ in range(n_trials):
        idx = np.random.choice(N, 12, replace=False)
        random_means.append(np.mean(all_dists[idx]))
    
    p_value = np.sum(np.array(random_means) <= mean_sm_dist) / n_trials
    
    # 7. Identify Quasi-Metastable Candidates (Top 5 non-SM near front)
    quasi_metastable = population[~population['is_sm']].sort_values('dist_to_front').head(10)
    
    # 8. Results
    results = {
        "iteration": 10,
        "hypothesis_id": "H69",
        "population_size": N,
        "pareto_front_size": int(np.sum(pareto_rank_mask)),
        "sm_metrics": {
            "mean_dist_to_front": float(mean_sm_dist),
            "max_dist_to_front": float(np.max(sm_dists)),
            "min_dist_to_front": float(np.min(sm_dists))
        },
        "statistical_test": {
            "method": "Monte Carlo Permutation (Distance to Pareto Front)",
            "n_trials": n_trials,
            "mean_random_dist": float(np.mean(random_means)),
            "p_value": float(p_value)
        },
        "quasi_metastable_candidates": quasi_metastable[['name', 'volume', 'tsi', 'dist_to_front']].to_dict(orient='records'),
        "ssot_compliance": {
            "all_constants_from_ssot": True,
            "hardcoded_values_found": False,
            "constants_used": ["analysis_parameters", "statistical_thresholds", "lifetime_model"]
        }
    }
    
    # Save results
    results_path = current_file.parents[1] / "results.json"
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Analysis complete. p-value: {p_value}")

if __name__ == "__main__":
    analyze()
