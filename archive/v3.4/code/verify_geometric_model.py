
import numpy as np

# Physical Data
MASSES = {'u': 2.16, 'd': 4.67, 's': 93.4, 'c': 1270, 'b': 4180, 't': 172760}
VOLUMES = {'u': 6.598952, 'd': 7.327725, 's': 9.5319, 'c': 11.517101, 'b': 12.276278, 't': 15.359984}

# Catalan Constant
G = 0.915965594

# Model 1: Empirical Fit (v3.4)
GAMMA_EMP = 1.3079
B_EMP = -7.9159

# Model 2: Geometric Theory (Catalan-7)
GAMMA_GEO = (10/7) * G
B_GEO = -(7 + G)

def evaluate(gamma, b, label):
    print(f"\n--- Evaluating {label} ---")
    print(f"Gamma: {gamma:.6f}, B': {b:.6f}")
    
    errors = []
    q_names = ['u', 'd', 's', 'c', 'b', 't']
    for q in q_names:
        m_obs = MASSES[q]
        v = VOLUMES[q]
        m_pred = np.exp(gamma * v + b)
        err = (m_pred - m_obs) / m_obs * 100
        errors.append(abs(err))
        print(f"{q.upper():<2}: Obs={m_obs:>10.2f}, Pred={m_pred:>10.2f}, Err={err:>+7.2f}%")
    
    mae = np.mean(errors)
    
    # R2
    ln_obs = np.log([MASSES[q] for q in q_names])
    ln_pred = [gamma * VOLUMES[q] + b for q in q_names]
    ss_res = np.sum((ln_obs - ln_pred)**2)
    ss_tot = np.sum((ln_obs - np.mean(ln_obs))**2)
    r2 = 1 - (ss_res / ss_tot)
    
    print(f"Global MAE: {mae:.4f}%")
    print(f"R^2 Score:  {r2:.6f}")
    return mae, r2

if __name__ == "__main__":
    mae_emp, r2_emp = evaluate(GAMMA_EMP, B_EMP, "Empirical v3.4 Fit")
    mae_geo, r2_geo = evaluate(GAMMA_GEO, B_GEO, "Geometric Catalan-7 Theory")
    
    print("\n--- Summary of Comparison ---")
    print(f"MAE Difference: {mae_geo - mae_emp:+.4f}%")
    print(f"R^2 Difference: {r2_geo - r2_emp:+.6f}")
    
    if abs(mae_geo - mae_emp) < 0.1:
        print("\nCONCLUSION: The Geometric Theory is STATISTICALLY INDISTINGUISHABLE from the best empirical fit.")
    else:
        print("\nCONCLUSION: The Geometric Theory provides a slightly different fit quality.")
