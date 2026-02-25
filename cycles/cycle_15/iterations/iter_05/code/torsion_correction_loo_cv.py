import sys
import json
import math
import time
from pathlib import Path
import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn.metrics import mean_absolute_error

# SSoT loader setup
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
ssot_path = project_root / "ssot"
sys.path.insert(0, str(ssot_path))    
from ksau_ssot import SSOT

def main():
    start_time = time.time()
    ssot = SSOT()
    consts = ssot.constants()
    params = ssot.parameters()
    topology = ssot.topology_assignments()
    
    # 1. Load constants from SSoT
    kappa = consts['mathematical_constants']['kappa']
    ev_model = consts['effective_volume_model']
    a_fixed = ev_model['a']
    b_fixed = ev_model['b']
    c_fixed = ev_model['c']
    
    # 2. Collect fermion data
    fermion_list = []
    # Combine leptons and quarks
    for sector in ['leptons', 'quarks']:
        for name, data in params[sector].items():
            if name in topology:
                topo = topology[name]
                v = topo['volume']
                n = topo['crossing_number']
                det = topo['determinant']
                m_obs = data['observed_mass_mev']
                
                v_eff = v + a_fixed * n + b_fixed * np.log(det) + c_fixed
                
                fermion_list.append({
                    "name": name,
                    "ln_m_obs": np.log(m_obs),
                    "v_eff": v_eff,
                    "ln_st": np.log(det)
                })
                
    df = pd.DataFrame(fermion_list)
    
    # 3. Calculate Residuals
    # Δln(m) = ln(m_obs) - κ * V_eff
    df['residual'] = df['ln_m_obs'] - kappa * df['v_eff']
    
    # 4. Standard OLS Regression
    X = df['ln_st']
    X_with_const = sm.add_constant(X)
    y = df['residual']
    
    model = sm.OLS(y, X_with_const).fit()
    
    alpha = model.params['ln_st']
    beta = model.params['const']
    p_value = model.pvalues['ln_st']
    r_squared = model.rsquared
    
    # 5. Leave-One-Out Cross-Validation (LOO-CV)
    loo_predictions = []
    for i in range(len(df)):
        train_df = df.drop(df.index[i])
        test_df = df.iloc[[i]]
        
        X_train = sm.add_constant(train_df['ln_st'])
        y_train = train_df['residual']
        
        # Fit model on N-1 points
        loo_model = sm.OLS(y_train, X_train).fit()
        
        # Predict on the left-out point
        X_test = [1.0, test_df['ln_st'].values[0]]
        pred = loo_model.predict(X_test)[0]
        loo_predictions.append(pred)
        
    df['loo_pred'] = loo_predictions
    df['loo_error'] = df['residual'] - df['loo_pred']
    
    training_mae = mean_absolute_error(df['residual'], model.predict(X_with_const))
    loo_mae = mean_absolute_error(df['residual'], df['loo_pred'])
    
    # 6. Monte Carlo Permutation Test (FPR)
    n_trials = 10000
    random_seed = 42
    np.random.seed(random_seed)
    r2_shuffled = []
    y_values = y.values.copy()
    for _ in range(n_trials):
        np.random.shuffle(y_values)
        shuffled_model = sm.OLS(y_values, X_with_const).fit()
        r2_shuffled.append(shuffled_model.rsquared)
    fpr = np.sum(np.array(r2_shuffled) >= r_squared) / n_trials
    
    # 7. Result Construction
    results = {
        "iteration": 5,
        "hypothesis_id": "H38",
        "timestamp": pd.Timestamp.now().isoformat(),
        "task_name": "自由度 2 (α, β) の線形補正モデルの検証",
        "data_sources": {
            "description": "Fermion masses and topologies via SSoT",
            "loaded_via_ssot": True
        },
        "computed_values": {
            "fixed_kappa": kappa,
            "v_eff_coefficients": {"a": a_fixed, "b": b_fixed, "c": c_fixed},
            "regression": {
                "alpha_slope": float(alpha),
                "beta_intercept": float(beta),
                "r_squared": float(r_squared),
                "p_value_alpha": float(p_value),
                "fpr": float(fpr)
            },
            "cross_validation": {
                "training_mae": float(training_mae),
                "loo_mae": float(loo_mae),
                "mae_ratio": float(loo_mae / training_mae) if training_mae > 0 else 0.0
            },
            "n_samples": len(df)
        },
        "ssot_compliance": {
            "all_constants_from_ssot": True,
            "hardcoded_values_found": False,
            "synthetic_data_used": False,
            "constants_used": ["mathematical_constants.kappa", "effective_volume_model", "particle_data", "topology_assignments"]
        },
        "reproducibility": {
            "random_seed": random_seed,
            "computation_time_sec": time.time() - start_time
        },
        "notes": "Validation includes LOO-CV to assess predictive stability. SSoT coefficients used."
    }
    
    results_path = current_file.parent.parent / "results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    print(f"H38 Iteration 5 results saved. R^2={r_squared:.4f}, LOO-MAE={loo_mae:.4f}")

if __name__ == "__main__":
    main()
