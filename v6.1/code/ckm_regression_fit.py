"""
CKM Regression Fitting
Fits coefficients A, B, beta, gamma, C to maximize R^2
Tests multiple formula variants
"""
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.metrics import r2_score

def load_features():
    """Load geometric features from diagnostic"""
    df = pd.read_csv('ckm_geometric_features.csv')
    return df

def model_logit(params, dV, dlnJ, V_bar):
    """
    Logit model: logit(V_ij) = C + A*dV + B*dlnJ + beta/V_bar + gamma*(dV*dlnJ)
    """
    A, B, beta, gamma, C = params
    logit_pred = C + A*dV + B*dlnJ + beta/V_bar + gamma*(dV*dlnJ)
    # Inverse logit (sigmoid)
    V_pred = 1.0 / (1.0 + np.exp(-logit_pred))
    return V_pred

def model_logit_no_interaction(params, dV, dlnJ, V_bar):
    """
    Without gamma interaction term
    """
    A, B, beta, C = params
    logit_pred = C + A*dV + B*dlnJ + beta/V_bar
    V_pred = 1.0 / (1.0 + np.exp(-logit_pred))
    return V_pred

def model_ln(params, dV, dlnJ, V_bar):
    """
    Linear in log-space: ln(V_ij) = C + A*dV + B*dlnJ + beta/V_bar
    """
    A, B, beta, C = params
    ln_pred = C + A*dV + B*dlnJ + beta/V_bar
    V_pred = np.exp(ln_pred)
    # Clip to [0, 1]
    V_pred = np.clip(V_pred, 1e-10, 1 - 1e-10)
    return V_pred

def model_exponential(params, dV, dlnJ, V_bar):
    """
    Exponential: V_ij = exp(A*dV + B*dlnJ + beta/V_bar + C)
    """
    A, B, beta, C = params
    V_pred = np.exp(A*dV + B*dlnJ + beta/V_bar + C)
    V_pred = np.clip(V_pred, 1e-10, 1 - 1e-10)
    return V_pred

def objective_r2(params, model_func, dV, dlnJ, V_bar, V_obs):
    """
    Objective: minimize negative R^2 (to maximize R^2)
    """
    V_pred = model_func(params, dV, dlnJ, V_bar)
    r2 = r2_score(V_obs, V_pred)
    return -r2  # Minimize negative = maximize R^2

def objective_mse(params, model_func, dV, dlnJ, V_bar, V_obs):
    """
    Objective: minimize MSE
    """
    V_pred = model_func(params, dV, dlnJ, V_bar)
    mse = np.mean((V_obs - V_pred)**2)
    return mse

def fit_model(model_func, n_params, dV, dlnJ, V_bar, V_obs, model_name):
    """
    Fit model using optimization
    """
    print(f"\n{'='*80}")
    print(f"Fitting: {model_name}")
    print(f"{'='*80}")

    # Initial guess
    if n_params == 5:
        x0 = [-1.5, -15.0, -68.0, 1.7, 16.0]  # A, B, beta, gamma, C
    elif n_params == 4:
        x0 = [-1.5, -15.0, -68.0, 16.0]  # A, B, beta, C
    else:
        raise ValueError("Invalid n_params")

    # Optimize for R^2
    result = minimize(
        objective_r2,
        x0,
        args=(model_func, dV, dlnJ, V_bar, V_obs),
        method='Nelder-Mead',
        options={'maxiter': 5000, 'xatol': 1e-8, 'fatol': 1e-8}
    )

    params_opt = result.x
    V_pred = model_func(params_opt, dV, dlnJ, V_bar)
    r2 = r2_score(V_obs, V_pred)
    mse = np.mean((V_obs - V_pred)**2)
    mae = np.mean(np.abs(V_obs - V_pred))

    # Print results
    if n_params == 5:
        A, B, beta, gamma, C = params_opt
        print(f"  A (barrier):    {A:>10.4f}")
        print(f"  B (entropy):    {B:>10.4f}")
        print(f"  beta (tunnel):  {beta:>10.4f}")
        print(f"  gamma (interact): {gamma:>10.4f}")
        print(f"  C (intercept):  {C:>10.4f}")
    else:
        A, B, beta, C = params_opt
        print(f"  A (barrier):    {A:>10.4f}")
        print(f"  B (entropy):    {B:>10.4f}")
        print(f"  beta (tunnel):  {beta:>10.4f}")
        print(f"  C (intercept):  {C:>10.4f}")

    print(f"\n  R^2:  {r2:.4f}")
    print(f"  MSE:  {mse:.6f}")
    print(f"  MAE:  {mae:.4f}")

    # Show predictions
    print(f"\n  {'Obs':<10} {'Pred':<10} {'Error'}")
    print(f"  {'-'*30}")
    for obs, pred in zip(V_obs, V_pred):
        err = abs(obs - pred) / obs * 100
        print(f"  {obs:<10.4f} {pred:<10.4f} {err:>6.1f}%")

    return {
        'model': model_name,
        'params': params_opt,
        'r2': r2,
        'mse': mse,
        'mae': mae,
        'predictions': V_pred
    }

def main():
    print("="*80)
    print("CKM Coefficient Regression Fitting")
    print("="*80)

    # Load data
    df = load_features()

    dV = df['dV'].values
    dlnJ = df['dlnJ'].values
    V_bar = df['V_bar'].values
    V_obs = df['obs'].values

    print(f"\nDataset: {len(V_obs)} CKM elements")

    # Test models
    results = []

    # Model 1: Full logit with interaction
    res1 = fit_model(model_logit, 5, dV, dlnJ, V_bar, V_obs,
                     "Logit (5-param): logit(V) = C + A*dV + B*dlnJ + beta/V_bar + gamma*(dV*dlnJ)")
    results.append(res1)

    # Model 2: Logit without interaction
    res2 = fit_model(model_logit_no_interaction, 4, dV, dlnJ, V_bar, V_obs,
                     "Logit (4-param): logit(V) = C + A*dV + B*dlnJ + beta/V_bar")
    results.append(res2)

    # Model 3: Linear in log-space
    res3 = fit_model(model_ln, 4, dV, dlnJ, V_bar, V_obs,
                     "Log-linear: ln(V) = C + A*dV + B*dlnJ + beta/V_bar")
    results.append(res3)

    # Model 4: Pure exponential
    res4 = fit_model(model_exponential, 4, dV, dlnJ, V_bar, V_obs,
                     "Exponential: V = exp(A*dV + B*dlnJ + beta/V_bar + C)")
    results.append(res4)

    # Summary
    print("\n" + "="*80)
    print("MODEL COMPARISON")
    print("="*80)
    print(f"{'Model':<50} | {'R^2':<8} | {'MSE':<10} | {'MAE'}")
    print("-"*80)
    for res in results:
        print(f"{res['model']:<50} | {res['r2']:<8.4f} | {res['mse']:<10.6f} | {res['mae']:.4f}")

    # Best model
    best = max(results, key=lambda x: x['r2'])
    print(f"\n{'='*80}")
    print(f"BEST MODEL: {best['model']}")
    print(f"  R^2 = {best['r2']:.4f}")
    print(f"{'='*80}")

    # Save best results
    with open('ckm_best_fit.txt', 'w') as f:
        f.write(f"Best CKM Model: {best['model']}\n")
        f.write(f"R^2: {best['r2']:.4f}\n")
        f.write(f"Parameters: {best['params']}\n")
    print("\nSaved best fit to ckm_best_fit.txt")

if __name__ == "__main__":
    main()
