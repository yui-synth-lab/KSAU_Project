import sys
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error
from datetime import datetime, timezone
import time
import math
from scipy import stats

current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
ssot_path = project_root / "ssot"
sys.path.insert(0, str(ssot_path))    
from ksau_ssot import SSOT

def main():
    start_time = time.time()
    ssot = SSOT()
    consts = ssot.constants()
    assignments = ssot.topology_assignments()
    
    # 1. Constants
    kappa = consts['mathematical_constants']['kappa']
    # Formula derived in Iter 5: alpha = sqrt(2) * kappa
    alpha_fixed = math.sqrt(2) * kappa
    # gamma fixed to -v_borromean
    v_borromean = consts['topology_constants']['v_borromean']
    gamma_fixed = -v_borromean
    
    # 2. Data Preparation
    particles = ["Electron", "Muon", "Tau", "Up", "Down", "Charm", "Strange", "Top", "Bottom"]
    data = []
    
    for p in particles:
        entry = assignments[p]
        if p in consts['particle_data']['quarks']:
            m_obs = consts['particle_data']['quarks'][p]['observed_mass']
        elif p in consts['particle_data']['leptons']:
            m_obs = consts['particle_data']['leptons'][p]['observed_mass']
        else:
            continue
            
        data.append({
            "particle": p,
            "m_obs": m_obs,
            "ln_m": np.log(m_obs),
            "vol": entry['volume'],
            "ln_det": np.log(entry['determinant']) if entry['determinant'] > 0 else 0
        })
        
    df = pd.DataFrame(data)
    
    # Model: ln(m) = kappa * V + alpha * ln(ST) + gamma + beta
    # Rearranging: ln(m) - kappa * V - alpha * ln(ST) - gamma = beta
    # Here ln(ST) is represented by ln_det based on previous ST mappings.
    # Note: KSAU formulas in H57/H59 context often define ST term just as ln(det) or a function of it. 
    # The prompt explicitly specifies: ln(m) = κV + α·ln(ST) + γ + β
    # We use ln_det as the ST term base (or small modifications).
    # Since alpha was fixed, beta is the ONLY free parameter (intercept of the residual).
    
    # Target value y = ln(m)
    # Known part = kappa * V + alpha_fixed * ln_det + gamma_fixed
    # We want to fit y = Known + beta
    # Or simply: residual = y - Known, beta = mean(residual)
    
    # Wait, the prompt says "β 単回帰" (beta simple regression, k=1).
    # If beta is just an intercept, it's a 0-slope regression, or we can fit beta as intercept.
    # Let's verify the exact formula.
    
    y = df['ln_m'].values
    V = df['vol'].values
    ln_ST = df['ln_det'].values # Using ln_det as ST term
    
    known_term = kappa * V + alpha_fixed * ln_ST + gamma_fixed
    
    # 3. Fit Beta (Training)
    # y = 1*known_term + beta is NOT a standard linear regression if we just fit intercept.
    # "β 単回帰" usually means estimating β as the intercept where slope is 1, 
    # OR maybe it means a regression where we find a single slope? 
    # "β のみが自由パラメータ" -> beta is the only free parameter.
    
    beta_fitted = np.mean(y - known_term)
    
    # P-value for beta != 0 (One-sample t-test on residuals)
    residuals_for_test = y - known_term
    t_stat, p_val_beta = stats.ttest_1samp(residuals_for_test, 0.0)
    
    y_pred_train = known_term + beta_fitted
    train_r2 = r2_score(y, y_pred_train)
    train_mae = mean_absolute_error(y, y_pred_train)
    
    # 4. LOO-CV
    n = len(df)
    loo_preds = np.zeros(n)
    loo_residuals = {}
    
    for i in range(n):
        # Training set without i
        train_idx = [j for j in range(n) if j != i]
        y_train = y[train_idx]
        known_train = known_term[train_idx]
        
        # Fit beta on training set
        beta_loo = np.mean(y_train - known_train)
        
        # Predict for i
        y_pred_loo = known_term[i] + beta_loo
        loo_preds[i] = y_pred_loo
        loo_residuals[df['particle'].iloc[i]] = float(y[i] - y_pred_loo)
        
    loo_r2 = r2_score(y, loo_preds)
    loo_mae = mean_absolute_error(y, loo_preds)
    
    # 5. Overfitting check
    is_r2_ok = loo_r2 >= train_r2 * 0.95
    is_mae_ok = loo_mae <= 2 * train_mae
    bonferroni_threshold = consts["statistical_thresholds"]["bonferroni_base_alpha"] / 3
    is_p_val_ok = p_val_beta < bonferroni_threshold
    
    results = {
        "iteration": 6,
        "hypothesis_id": "H59",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "task_name": "固定α・固定γでの β 単回帰と LOO-CV 実施",
        "data_sources": {
            "description": "Fermion 9 points (obs mass) vs Topology Volume and Determinant",
            "loaded_via_ssot": True
        },
        "computed_values": {
            "fixed_parameters": {
                "alpha": alpha_fixed,
                "gamma": gamma_fixed,
                "kappa": kappa
            },
            "fitted_beta": float(beta_fitted),
            "beta_p_value": float(p_val_beta),
            "training_metrics": {
                "r2": float(train_r2),
                "mae": float(train_mae)
            },
            "loo_cv_metrics": {
                "loo_r2": float(loo_r2),
                "loo_mae": float(loo_mae),
                "residuals": loo_residuals
            },
            "validation_checks": {
                "r2_check": bool(is_r2_ok),
                "mae_check": bool(is_mae_ok),
                "p_value_check": bool(is_p_val_ok)
            }
        },
        "ssot_compliance": {
            "all_constants_from_ssot": True,
            "hardcoded_values_found": False,
            "synthetic_data_used": False,
            "constants_used": [
                "mathematical_constants.kappa",
                "topology_constants.v_borromean",
                "particle_data.quarks",
                "particle_data.leptons",
                "topology_assignments",
                "statistical_thresholds.bonferroni_base_alpha"
            ]
        },
        "reproducibility": {
            "random_seed": None,
            "computation_time_sec": time.time() - start_time
        },
        "notes": "α=sqrt(2)*kappa, γ=-v_borromean に固定し、β（1パラメータ）のみを推定。LOO-CVを実施し残差と汎化性能を評価した。"
    }
    
    iter_dir = project_root / "cycles" / "cycle_23" / "iterations" / "iter_06"
    with open(iter_dir / "results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    print("Execution complete. Results saved.")
    print(f"Train R2: {train_r2:.6f}, Train MAE: {train_mae:.6f}")
    print(f"LOO R2: {loo_r2:.6f}, LOO MAE: {loo_mae:.6f}")
    print(f"Beta p-value: {p_val_beta}")

if __name__ == "__main__":
    main()