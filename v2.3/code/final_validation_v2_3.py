import pandas as pd
import numpy as np
import os
import sys

# Import the validation tools
sys.path.append("KSAU/publish/v2.3/code")
from ksau_validation_tools import LinkSelector, KSAUValidator, plot_mass_predictions, plot_null_hypothesis_test
from advanced_bayesian_analysis import BayesianValidator, FalsePositiveAnalyzer

# 1. Prepare the Enhanced Database
print("Step 1: Preparing Enhanced Candidate Database...")
input_path = "KSAU/publish/v2.3/data/link_candidates_3comp.csv"
df_cand = pd.read_csv(input_path)

df_cand = df_cand.rename(columns={'name': 'LinkID', 'crossing_number': 'Crossings', 'volume': 'Vol', 'signature': 'Sig_pi'})

def get_l_tot(matrix_str):
    try:
        nums = [int(s) for s in matrix_str.replace('{','').replace('}','').replace(',',' ').split() if s.lstrip('-').isdigit()]
        return sum([abs(n) for n in nums]) // 2
    except: return 0

df_cand['L_tot'] = df_cand['linking_matrix'].apply(get_l_tot)
df_cand['Writhe'] = (df_cand['Sig_pi'] + df_cand['L_tot']) / 2.0
df_cand['Components'] = 3

# 2. Automated Selection
print("\nStep 2: Performing Deterministic Link Selection...")
selector = LinkSelector(df_cand)
params = {'alpha': 1.0, 'beta_sig': -0.56, 'gamma_L': 0.64, 'intercept': -5.3}
assignments = selector.select_all_quarks(params, method='topological_ordering')

# 3. Statistical Validation
print("\nStep 3: Statistical Validation & Null Hypothesis Testing...")
validator = KSAUValidator(assignments, df_cand)
results = validator.fit_regression(['Vol', 'Sig', 'L'])
ksau_r2 = results['r_squared']
print(f"KSAU R²: {ksau_r2:.4f}")

# Null Hypothesis
print("Running 1000 random trials...")
null_results = validator.null_hypothesis_test(df_cand, n_trials=1000, include_features=['Vol', 'Sig', 'L'])
print(f"Frequentist P-Value: {null_results['p_value']:.4f}")

# 4. Bayesian Analysis
print("\nStep 4: Bayesian Analysis...")
bayesian = BayesianValidator(ksau_r2, null_results['distribution'], n_particles=6)
bf_result = bayesian.calculate_bayes_factor(method='likelihood_ratio')
print(f"Bayes Factor (LR): {bf_result['bayes_factor']:.2f}")
print(f"Interpretation: {bf_result['interpretation']}")
print(f"Equivalent Significance: {bf_result['evidence_strength']:.2f} sigma")

# 5. False Positive Clustering Analysis
print("\nStep 5: False Positive Clustering Analysis...")
# Extract false positives (assignments that met or beat KSAU R2)
high_r2_indices = np.where(null_results['distribution'] >= ksau_r2)[0]
false_positives = [null_results['random_assignments'][i] for i in high_r2_indices]

if len(false_positives) > 0:
    analyzer = FalsePositiveAnalyzer(assignments, false_positives, df_cand)
    cluster_results = analyzer.cluster_analysis()
    patterns = analyzer.analyze_patterns()
    print(f"Found {len(false_positives)} false positives.")
    print(f"Clustering: {cluster_results['neighbors']} neighbors (d<=2)")
    print(f"Stability: Most stable quark is '{patterns['most_stable']}'")
else:
    print("No false positives found (P=0). Exceptional significance!")

# 6. Save Artifacts
print("\nStep 6: Saving Visualizations...")
out_dir = "KSAU/publish/v2.3/figures/validation"
os.makedirs(out_dir, exist_ok=True)

plot_mass_predictions(validator, results, save_path=f"{out_dir}/v2.3_mass_fit_official.png")
plot_null_hypothesis_test(null_results, save_path=f"{out_dir}/v2.3_p_value_test.png")
bayesian.plot_evidence(save_path=f"{out_dir}/v2.3_bayesian_evidence.png")
if len(false_positives) > 0:
    analyzer.plot_analysis(save_path=f"{out_dir}/v2.3_clustering_analysis.png")

# 7. Final Assignments Export
pd.DataFrame.from_dict(assignments, orient='index', columns=['LinkID']).to_csv("KSAU/publish/v2.3/data/final_assignments_v2.3.csv")
print("\nValidation Complete. Results saved to KSAU/publish/v2.3/")
