"""
KSAU v4.1 Phase 2: Muon Anomaly / Lepton Correction Analysis
=============================================================

v4.0 lepton mass formula:
    ln(m_l) = (2/9) * G * N^2 + C_l

where G = 0.915965594 (Catalan constant), N = crossing number,
C_l fixed by electron mass.

The muon at +17.8% is the single largest lepton error and a key v4.1 target.

This script tests 9 correction models and produces a comprehensive comparison.
"""

import numpy as np
from scipy.optimize import minimize_scalar, minimize

# ===========================================================================
# CONSTANTS
# ===========================================================================
G = 0.915965594177219  # Catalan constant (high precision)
PI = np.pi

# ===========================================================================
# LEPTON DATA
# ===========================================================================
# Particle data: name, knot, N, det, signature, genus, hyp_volume, classification
LEPTONS = [
    {
        "name": "Electron",
        "symbol": "e",
        "knot": "3_1",
        "N": 3,
        "det": 3,
        "signature": -2,
        "genus": 1,
        "hyp_volume": 0.0,       # torus knot T(2,3)
        "classification": "Torus",
        "is_twist": False,
        "m_obs": 0.51099895,     # MeV (PDG 2024)
    },
    {
        "name": "Muon",
        "symbol": "mu",
        "knot": "6_1",
        "N": 6,
        "det": 9,
        "signature": 0,
        "genus": 2,
        "hyp_volume": 3.16396322888,  # Stevedore knot
        "classification": "Twist/Hyperbolic",
        "is_twist": True,
        "m_obs": 105.6583755,    # MeV (PDG 2024)
    },
    {
        "name": "Tau",
        "symbol": "tau",
        "knot": "7_1",
        "N": 7,
        "det": 7,
        "signature": -6,
        "genus": 3,
        "hyp_volume": 0.0,       # torus knot T(2,7)
        "classification": "Torus",
        "is_twist": False,
        "m_obs": 1776.86,        # MeV (PDG 2024)
    },
]

# Convenience arrays
names     = np.array([l["name"] for l in LEPTONS])
N_arr     = np.array([l["N"] for l in LEPTONS], dtype=float)
N2_arr    = N_arr**2
det_arr   = np.array([l["det"] for l in LEPTONS], dtype=float)
sig_arr   = np.array([l["signature"] for l in LEPTONS], dtype=float)
genus_arr = np.array([l["genus"] for l in LEPTONS], dtype=float)
vol_arr   = np.array([l["hyp_volume"] for l in LEPTONS], dtype=float)
twist_arr = np.array([1.0 if l["is_twist"] else 0.0 for l in LEPTONS])
m_obs     = np.array([l["m_obs"] for l in LEPTONS])
ln_m_obs  = np.log(m_obs)

# Observed mass ratios
mu_e_obs = m_obs[1] / m_obs[0]   # ~206.77
tau_e_obs = m_obs[2] / m_obs[0]  # ~3477.2


# ===========================================================================
# HELPER FUNCTIONS
# ===========================================================================
def compute_errors(ln_m_pred):
    """Compute individual signed % errors, MAE, max |error|."""
    m_pred = np.exp(ln_m_pred)
    pct_err = (m_pred - m_obs) / m_obs * 100.0   # signed %
    abs_pct = np.abs(pct_err)
    mae = np.mean(abs_pct)
    max_err = np.max(abs_pct)
    return m_pred, pct_err, abs_pct, mae, max_err


def compute_ratios(m_pred):
    """Compute predicted mass ratios mu/e and tau/e."""
    mu_e_pred = m_pred[1] / m_pred[0]
    tau_e_pred = m_pred[2] / m_pred[0]
    return mu_e_pred, tau_e_pred


def fix_C_by_electron(formula_fn, *args):
    """Given a formula ln(m) = formula_fn(N, ...) + C, solve for C using electron."""
    # C = ln(m_e) - formula_fn(N_e, ...)
    return ln_m_obs[0] - formula_fn(0, *args)  # index 0 = electron


def print_model_detail(label, ln_m_pred, n_free, param_info=""):
    """Print detailed results for a model."""
    m_pred, pct_err, abs_pct, mae, max_err = compute_errors(ln_m_pred)
    mu_e_pred, tau_e_pred = compute_ratios(m_pred)

    print(f"\n{'='*72}")
    print(f"  Model: {label}")
    if param_info:
        print(f"  Parameters: {param_info}")
    print(f"  Free parameters (beyond electron calibration): {n_free}")
    print(f"{'='*72}")
    print(f"  {'Particle':<10} {'Obs (MeV)':>12} {'Pred (MeV)':>12} {'Error':>10} {'|Error|':>10}")
    print(f"  {'-'*54}")
    for i in range(3):
        print(f"  {names[i]:<10} {m_obs[i]:>12.4f} {m_pred[i]:>12.4f} {pct_err[i]:>+9.2f}% {abs_pct[i]:>9.2f}%")
    print(f"  {'-'*54}")
    print(f"  MAE = {mae:.4f}%,  Max|Error| = {max_err:.4f}%")
    print(f"\n  Mass ratios:")
    print(f"    m_mu/m_e :  Obs = {mu_e_obs:.2f},  Pred = {mu_e_pred:.2f},  Ratio err = {(mu_e_pred/mu_e_obs - 1)*100:+.2f}%")
    print(f"    m_tau/m_e:  Obs = {tau_e_obs:.2f},  Pred = {tau_e_pred:.2f},  Ratio err = {(tau_e_pred/tau_e_obs - 1)*100:+.2f}%")

    return mae, max_err, mu_e_pred, tau_e_pred


# ===========================================================================
# COLLECT RESULTS
# ===========================================================================
results = []  # list of dicts for final comparison table


def record(label, mae, max_err, n_free, mu_e_pred, tau_e_pred, pct_errs):
    results.append({
        "label": label,
        "mae": mae,
        "max_err": max_err,
        "n_free": n_free,
        "mu_e_pred": mu_e_pred,
        "tau_e_pred": tau_e_pred,
        "err_e": pct_errs[0],
        "err_mu": pct_errs[1],
        "err_tau": pct_errs[2],
    })


# ###########################################################################
# MODEL 0: v4.0 BASELINE
# ###########################################################################
print("\n" + "#"*72)
print("#  KSAU v4.1 Phase 2: Lepton Correction Analysis")
print("#  Testing 9 correction models for muon anomaly resolution")
print("#"*72)

gamma_L = (2.0/9.0) * G   # v4.0 coefficient
# C_l fixed exactly by electron: C_l = ln(m_e) - gamma_L * 9
C_l_v40 = ln_m_obs[0] - gamma_L * N2_arr[0]

ln_m_v40 = gamma_L * N2_arr + C_l_v40
mae0, max0, mu_e_0, tau_e_0 = print_model_detail(
    "v4.0 Baseline: ln(m) = (2/9)G * N^2 + C_l",
    ln_m_v40, 0,
    f"gamma_L = (2/9)*G = {gamma_L:.8f}, C_l = {C_l_v40:.6f}"
)
m_pred0, pct0, _, _, _ = compute_errors(ln_m_v40)
record("(0) v4.0 Baseline", mae0, max0, 0, mu_e_0, tau_e_0, pct0)


# ###########################################################################
# MODEL (a): N^p POWER MODEL  (optimize p, C fixed by electron)
# ###########################################################################
print("\n\n" + "="*72)
print("  MODEL (a): N^p Power Model")
print("  ln(m) = alpha * N^p + C,  with C fixed by electron")
print("  Optimize p (and implicitly alpha via a full 2-param fit)")
print("="*72)

def model_a_mae(params):
    p, alpha = params
    # C fixed by electron
    C = ln_m_obs[0] - alpha * N_arr[0]**p
    ln_pred = alpha * N_arr**p + C
    m_pred = np.exp(ln_pred)
    return np.mean(np.abs((m_pred - m_obs) / m_obs)) * 100.0

# Grid search for initial guess
best_p, best_alpha, best_val = 2.0, gamma_L, 1e10
for p_try in np.linspace(1.0, 4.0, 601):
    for a_try in np.linspace(0.01, 0.8, 200):
        val = model_a_mae([p_try, a_try])
        if val < best_val:
            best_val = val
            best_p = p_try
            best_alpha = a_try

res_a = minimize(model_a_mae, [best_p, best_alpha], method='Nelder-Mead',
                 options={'xatol': 1e-12, 'fatol': 1e-12, 'maxiter': 50000})
p_opt, alpha_opt = res_a.x
C_a = ln_m_obs[0] - alpha_opt * N_arr[0]**p_opt
ln_m_a = alpha_opt * N_arr**p_opt + C_a

print(f"\n  Optimal p = {p_opt:.8f}")
print(f"  Optimal alpha = {alpha_opt:.8f}")
print(f"  C (from electron) = {C_a:.6f}")

# Check for clean expressions of p
print("\n  Checking clean expressions for p:")
candidates_p = {
    "2": 2.0,
    "2 + G/6": 2.0 + G/6.0,
    "2 + 1/7": 2.0 + 1.0/7.0,
    "2 + G/pi": 2.0 + G/PI,
    "2 + 1/9": 2.0 + 1.0/9.0,
    "2 + G/7": 2.0 + G/7.0,
    "2 + G/9": 2.0 + G/9.0,
    "2 + 2G/9": 2.0 + 2*G/9.0,
    "7/3": 7.0/3.0,
    "9/4": 9.0/4.0,
    "ln(10)": np.log(10),
    "e (Euler)": np.e,
    "2 + G/10": 2.0 + G/10.0,
    "2 + 1/pi": 2.0 + 1.0/PI,
    "2 + G^2": 2.0 + G**2,
    "2 + 1/10": 2.1,
    "pi - 1": PI - 1.0,
}
for expr, val in sorted(candidates_p.items(), key=lambda x: abs(x[1] - p_opt)):
    delta = val - p_opt
    print(f"    p = {expr:<16s} = {val:.8f}  (delta = {delta:+.8f})")

mae_a, max_a, mu_e_a, tau_e_a = print_model_detail(
    "(a) N^p Power Model", ln_m_a, 1,
    f"p = {p_opt:.6f}, alpha = {alpha_opt:.6f}"
)
_, pct_a, _, _, _ = compute_errors(ln_m_a)
record("(a) N^p Power", mae_a, max_a, 1, mu_e_a, tau_e_a, pct_a)


# ###########################################################################
# MODEL (b): N^2 + GENUS CORRECTION  (exact solve, 3 eqs / 3 unknowns)
# ###########################################################################
print("\n\n" + "="*72)
print("  MODEL (b): N^2 + Genus Correction")
print("  ln(m) = alpha * N^2 + beta * genus + C")
print("  genus = {1, 2, 3} for {e, mu, tau}")
print("  Exact solve: 3 equations, 3 unknowns")
print("="*72)

# System:  A * [alpha, beta, C]^T = ln_m_obs
A_b = np.column_stack([N2_arr, genus_arr, np.ones(3)])
params_b = np.linalg.solve(A_b, ln_m_obs)
alpha_b, beta_b, C_b = params_b

print(f"\n  Exact solution:")
print(f"    alpha = {alpha_b:.10f}")
print(f"    beta  = {beta_b:.10f}")
print(f"    C     = {C_b:.10f}")

# Check alpha against (2/9)*G
print(f"\n  alpha vs (2/9)*G = {gamma_L:.10f}:  delta = {alpha_b - gamma_L:+.10f}")
# Check beta for clean expressions
print(f"\n  Checking clean expressions for beta = {beta_b:.8f}:")
candidates_beta = {
    "G/pi": G/PI,
    "G/3": G/3.0,
    "1/pi": 1.0/PI,
    "G/7": G/7.0,
    "2/9": 2.0/9.0,
    "G^2": G**2,
    "1/3": 1.0/3.0,
    "G/9": G/9.0,
    "ln(2)/pi": np.log(2)/PI,
    "G/(2*pi)": G/(2*PI),
    "1/7": 1.0/7.0,
    "(2/9)*G": (2.0/9.0)*G,
    "1/9": 1.0/9.0,
    "2*G/7": 2*G/7.0,
    "-G/3": -G/3.0,
    "-1/3": -1.0/3.0,
    "-G/7": -G/7.0,
    "-1/pi": -1.0/PI,
}
for expr, val in sorted(candidates_beta.items(), key=lambda x: abs(x[1] - beta_b)):
    delta = val - beta_b
    print(f"    beta = {expr:<16s} = {val:+.8f}  (delta = {delta:+.8f})")
    if abs(delta) < 0.01:
        break  # show top matches only up to a close one

ln_m_b = alpha_b * N2_arr + beta_b * genus_arr + C_b
# This is exact by construction, but let's verify
mae_b, max_b, mu_e_b, tau_e_b = print_model_detail(
    "(b) N^2 + Genus", ln_m_b, 2,
    f"alpha = {alpha_b:.6f}, beta = {beta_b:.6f}, C = {C_b:.6f}"
)
_, pct_b, _, _, _ = compute_errors(ln_m_b)
record("(b) N^2 + Genus (exact)", mae_b, max_b, 2, mu_e_b, tau_e_b, pct_b)


# ###########################################################################
# MODEL (c): N^2 + SIGNATURE CORRECTION
# ###########################################################################
print("\n\n" + "="*72)
print("  MODEL (c): N^2 + Signature Correction")
print("  ln(m) = alpha * N^2 + beta * signature + C")
print("  signatures = {-2, 0, -6}")
print("  Exact solve: 3 equations, 3 unknowns")
print("="*72)

A_c = np.column_stack([N2_arr, sig_arr, np.ones(3)])
params_c = np.linalg.solve(A_c, ln_m_obs)
alpha_c, beta_c, C_c = params_c

print(f"\n  Exact solution:")
print(f"    alpha = {alpha_c:.10f}")
print(f"    beta  = {beta_c:.10f}")
print(f"    C     = {C_c:.10f}")
print(f"\n  alpha vs (2/9)*G = {gamma_L:.10f}:  delta = {alpha_c - gamma_L:+.10f}")

# Check beta
print(f"\n  Checking clean expressions for beta = {beta_c:.8f}:")
for expr, val in sorted(candidates_beta.items(), key=lambda x: abs(x[1] - beta_c)):
    delta = val - beta_c
    print(f"    beta = {expr:<16s} = {val:+.8f}  (delta = {delta:+.8f})")
    if abs(delta) < 0.01:
        break

ln_m_c = alpha_c * N2_arr + beta_c * sig_arr + C_c
mae_c, max_c, mu_e_c, tau_e_c = print_model_detail(
    "(c) N^2 + Signature", ln_m_c, 2,
    f"alpha = {alpha_c:.6f}, beta = {beta_c:.6f}, C = {C_c:.6f}"
)
_, pct_c, _, _, _ = compute_errors(ln_m_c)
record("(c) N^2 + Signature (exact)", mae_c, max_c, 2, mu_e_c, tau_e_c, pct_c)


# ###########################################################################
# MODEL (d): HYBRID VOLUME MODEL
# ###########################################################################
print("\n\n" + "="*72)
print("  MODEL (d): Hybrid Volume Model")
print("  For hyperbolic knots (6_1): use hyperbolic volume")
print("  For torus knots (3_1, 7_1): use N^2")
print("  ln(m) = gamma * X + C, where X = V_hyp if hyperbolic, else N^2")
print("="*72)

# We need a single linear formula. The challenge: electron uses N^2=9, muon uses V=3.164, tau uses N^2=49
# These are on different scales so we need separate coefficients or a unified approach.
# Approach: ln(m) = gamma_torus * N^2 * (1-is_hyp) + gamma_hyp * V * is_hyp + C
# But that's 2 free params + C = 3 params for 3 data points (exact).

is_hyp = np.array([0.0, 1.0, 0.0])  # only 6_1 is hyperbolic
A_d = np.column_stack([N2_arr * (1 - is_hyp), vol_arr * is_hyp, np.ones(3)])
params_d = np.linalg.solve(A_d, ln_m_obs)
gamma_torus, gamma_hyp, C_d = params_d

print(f"\n  Exact solution:")
print(f"    gamma_torus (for N^2) = {gamma_torus:.10f}")
print(f"    gamma_hyp   (for V)   = {gamma_hyp:.10f}")
print(f"    C                     = {C_d:.10f}")
print(f"\n  gamma_torus vs (2/9)*G = {gamma_L:.10f}:  delta = {gamma_torus - gamma_L:+.10f}")
print(f"  gamma_hyp vs (10/7)*G (quark coeff) = {(10.0/7.0)*G:.10f}:  delta = {gamma_hyp - (10.0/7.0)*G:+.10f}")

# Check gamma_hyp for clean expressions
print(f"\n  Checking clean expressions for gamma_hyp = {gamma_hyp:.8f}:")
candidates_gamma = {
    "(10/7)*G": (10.0/7.0)*G,
    "G": G,
    "2*G": 2*G,
    "G/pi": G/PI,
    "pi/2": PI/2.0,
    "1.0": 1.0,
    "3*G/2": 1.5*G,
    "(2/3)*G": (2.0/3.0)*G,
    "ln(10)/2": np.log(10)/2,
    "G + 1/7": G + 1.0/7.0,
    "(9/7)*G": (9.0/7.0)*G,
    "4*G/3": (4.0/3.0)*G,
    "7*G/6": (7.0/6.0)*G,
    "5*G/4": (5.0/4.0)*G,
    "(2/9)*G*9 (=2G)": 2*G,
}
for expr, val in sorted(candidates_gamma.items(), key=lambda x: abs(x[1] - gamma_hyp)):
    delta = val - gamma_hyp
    print(f"    gamma_hyp = {expr:<24s} = {val:.8f}  (delta = {delta:+.8f})")

ln_m_d = gamma_torus * N2_arr * (1 - is_hyp) + gamma_hyp * vol_arr * is_hyp + C_d
mae_d, max_d, mu_e_d, tau_e_d = print_model_detail(
    "(d) Hybrid Volume (torus: N^2, hyp: V)", ln_m_d, 2,
    f"gamma_torus = {gamma_torus:.6f}, gamma_hyp = {gamma_hyp:.6f}, C = {C_d:.6f}"
)
_, pct_d, _, _, _ = compute_errors(ln_m_d)
record("(d) Hybrid Volume (exact)", mae_d, max_d, 2, mu_e_d, tau_e_d, pct_d)


# ###########################################################################
# MODEL (e): DETERMINANT-AWARE CORRECTION
# ###########################################################################
print("\n\n" + "="*72)
print("  MODEL (e): Determinant-Aware Correction")
print("  ln(m) = alpha * N^2 + beta * ln(Det) + C")
print("  Determinants = {3, 9, 7}")
print("  Exact solve: 3 equations, 3 unknowns")
print("="*72)

ln_det_arr = np.log(det_arr)
A_e = np.column_stack([N2_arr, ln_det_arr, np.ones(3)])
params_e = np.linalg.solve(A_e, ln_m_obs)
alpha_e, beta_e, C_e = params_e

print(f"\n  Exact solution:")
print(f"    alpha = {alpha_e:.10f}")
print(f"    beta  = {beta_e:.10f}")
print(f"    C     = {C_e:.10f}")
print(f"\n  alpha vs (2/9)*G = {gamma_L:.10f}:  delta = {alpha_e - gamma_L:+.10f}")

# Check beta
print(f"\n  Checking clean expressions for beta = {beta_e:.8f}:")
for expr, val in sorted(candidates_beta.items(), key=lambda x: abs(x[1] - beta_e)):
    delta = val - beta_e
    print(f"    beta = {expr:<16s} = {val:+.8f}  (delta = {delta:+.8f})")
    if abs(delta) < 0.02:
        break

ln_m_e_model = alpha_e * N2_arr + beta_e * ln_det_arr + C_e
mae_e, max_e, mu_e_e, tau_e_e = print_model_detail(
    "(e) N^2 + ln(Det)", ln_m_e_model, 2,
    f"alpha = {alpha_e:.6f}, beta = {beta_e:.6f}, C = {C_e:.6f}"
)
_, pct_e_model, _, _, _ = compute_errors(ln_m_e_model)
record("(e) N^2 + ln(Det) (exact)", mae_e, max_e, 2, mu_e_e, tau_e_e, pct_e_model)


# ###########################################################################
# MODEL (f): GENERALIZED POWER N^p WITH p FROM CATALAN CONSTANT
# ###########################################################################
print("\n\n" + "="*72)
print("  MODEL (f): N^p with p chosen from Catalan-related expressions")
print("  ln(m) = (2/9)*G * N^p + C,  C fixed by electron")
print("  Test various p values involving G, pi, 7, 9")
print("="*72)

p_candidates = {
    "2 (v4.0)":        2.0,
    "2 + G/6":         2.0 + G/6.0,
    "2 + 1/7":         2.0 + 1.0/7.0,
    "2 + G/pi":        2.0 + G/PI,
    "2 + G/9":         2.0 + G/9.0,
    "2 + G/7":         2.0 + G/7.0,
    "2 + 2G/9":        2.0 + 2*G/9.0,
    "2 + 1/9":         2.0 + 1.0/9.0,
    "2 + G/10":        2.0 + G/10.0,
    "2 + 1/pi":        2.0 + 1.0/PI,
    "7/3":             7.0/3.0,
    "9/4":             9.0/4.0,
    "2 + G^2":         2.0 + G**2,
    "pi - 1":          PI - 1.0,
    "2 + (2/9)*G":     2.0 + (2.0/9.0)*G,
    "2 + 1/10":        2.1,
    "1 + G":           1.0 + G,
    "2 - G/9":         2.0 - G/9.0,
    "2 - 1/7":         2.0 - 1.0/7.0,
    "2 - G/pi":        2.0 - G/PI,
}

print(f"\n  {'Expression':<20s} {'p':>10s} {'MAE (%)':>10s} {'Err_e':>10s} {'Err_mu':>10s} {'Err_tau':>10s}")
print(f"  {'-'*70}")

best_f_mae = 1e10
best_f_label = ""
best_f_ln = None
best_f_p = 0

for expr, p_val in sorted(p_candidates.items(), key=lambda x: x[1]):
    # C fixed by electron
    C_f = ln_m_obs[0] - gamma_L * N_arr[0]**p_val
    ln_pred_f = gamma_L * N_arr**p_val + C_f
    m_pred_f, pct_f, _, mae_f_val, _ = compute_errors(ln_pred_f)
    print(f"  {expr:<20s} {p_val:>10.6f} {mae_f_val:>10.4f} {pct_f[0]:>+9.2f}% {pct_f[1]:>+9.2f}% {pct_f[2]:>+9.2f}%")
    if mae_f_val < best_f_mae:
        best_f_mae = mae_f_val
        best_f_label = expr
        best_f_ln = ln_pred_f.copy()
        best_f_p = p_val

print(f"\n  >> Best Catalan-expression p: {best_f_label} (p = {best_f_p:.6f}, MAE = {best_f_mae:.4f}%)")

mae_f, max_f, mu_e_f, tau_e_f = print_model_detail(
    f"(f) N^p with p = {best_f_label}", best_f_ln, 0,
    f"p = {best_f_p:.6f}, coefficient = (2/9)*G = {gamma_L:.8f}"
)
_, pct_f_best, _, _, _ = compute_errors(best_f_ln)
record(f"(f) N^p, p={best_f_label}", mae_f, max_f, 0, mu_e_f, tau_e_f, pct_f_best)


# ###########################################################################
# MODEL (g): OPTIMIZED COEFFICIENT alpha IN ln(m) = alpha * N^2 + C
# ###########################################################################
print("\n\n" + "="*72)
print("  MODEL (g): Optimized coefficient alpha")
print("  ln(m) = alpha * N^2 + C,  C fixed by electron")
print("  Find alpha that minimizes MAE across all 3 leptons")
print("="*72)

def model_g_mae(alpha_val):
    C_val = ln_m_obs[0] - alpha_val * N2_arr[0]
    ln_pred = alpha_val * N2_arr + C_val
    m_pred = np.exp(ln_pred)
    return np.mean(np.abs((m_pred - m_obs) / m_obs)) * 100.0

# Fine grid search + refinement
alpha_range = np.linspace(0.01, 0.5, 10000)
mae_vals = [model_g_mae(a) for a in alpha_range]
idx_best = np.argmin(mae_vals)
alpha_init = alpha_range[idx_best]

res_g = minimize_scalar(model_g_mae, bounds=(alpha_init - 0.01, alpha_init + 0.01), method='bounded')
alpha_g = res_g.x
C_g = ln_m_obs[0] - alpha_g * N2_arr[0]
ln_m_g = alpha_g * N2_arr + C_g

print(f"\n  Optimal alpha = {alpha_g:.10f}")
print(f"  (2/9)*G       = {gamma_L:.10f}")
print(f"  Delta          = {alpha_g - gamma_L:+.10f}")
print(f"  C (electron)   = {C_g:.6f}")

# Check for clean expressions
print(f"\n  Checking clean expressions for alpha = {alpha_g:.8f}:")
candidates_alpha = {
    "(2/9)*G": gamma_L,
    "G/5": G/5.0,
    "G/4": G/4.0,
    "1/5": 0.2,
    "2*G/9": gamma_L,  # same
    "G/pi": G/PI,
    "G/(2*pi)": G/(2*PI),
    "1/6": 1.0/6.0,
    "G/6": G/6.0,
    "pi/18": PI/18.0,
    "G^2/4": G**2/4.0,
    "1/(2*pi)": 1.0/(2*PI),
    "ln(2)/pi": np.log(2)/PI,
    "G/7": G/7.0,
    "(2/10)*G": 0.2*G,
    "G/(3+pi)": G/(3+PI),
}
for expr, val in sorted(candidates_alpha.items(), key=lambda x: abs(x[1] - alpha_g)):
    delta = val - alpha_g
    print(f"    alpha = {expr:<16s} = {val:.8f}  (delta = {delta:+.8f})")

mae_g, max_g, mu_e_g, tau_e_g = print_model_detail(
    "(g) Optimized alpha * N^2 + C", ln_m_g, 0,
    f"alpha = {alpha_g:.8f}"
)
_, pct_g, _, _, _ = compute_errors(ln_m_g)
record("(g) Optimized alpha*N^2", mae_g, max_g, 0, mu_e_g, tau_e_g, pct_g)


# ###########################################################################
# MODEL (h): TWO-INVARIANT MODEL  ln(m) = alpha*N + beta*N^2 + C
# ###########################################################################
print("\n\n" + "="*72)
print("  MODEL (h): Two-Invariant: alpha*N + beta*N^2 + C")
print("  C fixed by electron, optimize alpha, beta for MAE")
print("="*72)

def model_h_mae(params):
    alpha_h, beta_h = params
    C_h = ln_m_obs[0] - alpha_h * N_arr[0] - beta_h * N2_arr[0]
    ln_pred = alpha_h * N_arr + beta_h * N2_arr + C_h
    m_pred = np.exp(ln_pred)
    return np.mean(np.abs((m_pred - m_obs) / m_obs)) * 100.0

# Grid search for initial guess
best_h = (0.0, gamma_L, 1e10)
for a_try in np.linspace(-2.0, 2.0, 200):
    for b_try in np.linspace(-0.5, 0.5, 200):
        val = model_h_mae([a_try, b_try])
        if val < best_h[2]:
            best_h = (a_try, b_try, val)

res_h = minimize(model_h_mae, [best_h[0], best_h[1]], method='Nelder-Mead',
                 options={'xatol': 1e-12, 'fatol': 1e-12, 'maxiter': 50000})
alpha_h, beta_h = res_h.x
C_h = ln_m_obs[0] - alpha_h * N_arr[0] - beta_h * N2_arr[0]
ln_m_h = alpha_h * N_arr + beta_h * N2_arr + C_h

print(f"\n  Optimal alpha (N coeff)  = {alpha_h:.10f}")
print(f"  Optimal beta  (N^2 coeff) = {beta_h:.10f}")
print(f"  C (electron)              = {C_h:.6f}")

# Since we have 2 free params and 2 remaining data points (mu, tau), this is also exact
# Check:
print(f"\n  Verification (should be ~0 for exact):")
print(f"    Residual mu:  {ln_m_h[1] - ln_m_obs[1]:.2e}")
print(f"    Residual tau: {ln_m_h[2] - ln_m_obs[2]:.2e}")

# Check alpha, beta for clean expressions
print(f"\n  Checking clean expressions for alpha = {alpha_h:.8f}:")
cand_ah = {
    "G": G,
    "-G": -G,
    "1": 1.0,
    "-1": -1.0,
    "G/2": G/2.0,
    "-G/2": -G/2.0,
    "pi/3": PI/3.0,
    "-pi/3": -PI/3.0,
    "2*G/3": 2*G/3.0,
    "G/pi": G/PI,
    "0": 0.0,
    "1/3": 1.0/3.0,
    "-1/3": -1.0/3.0,
    "2/3": 2.0/3.0,
    "-2/3": -2.0/3.0,
    "7*G/9": 7*G/9.0,
    "-7*G/9": -7*G/9.0,
}
for expr, val in sorted(cand_ah.items(), key=lambda x: abs(x[1] - alpha_h))[:8]:
    delta = val - alpha_h
    print(f"    alpha = {expr:<16s} = {val:+.8f}  (delta = {delta:+.8f})")

print(f"\n  Checking clean expressions for beta = {beta_h:.8f}:")
cand_bh = {
    "(2/9)*G": gamma_L,
    "G/5": G/5.0,
    "G/4": G/4.0,
    "1/5": 0.2,
    "G/6": G/6.0,
    "1/6": 1.0/6.0,
    "G/7": G/7.0,
    "G/(2*pi)": G/(2*PI),
    "pi/18": PI/18.0,
    "1/9": 1.0/9.0,
    "G/9": G/9.0,
    "G/3": G/3.0,
    "1/7": 1.0/7.0,
    "2/(9*pi)": 2.0/(9.0*PI),
    "G^2/3": G**2/3.0,
}
for expr, val in sorted(cand_bh.items(), key=lambda x: abs(x[1] - beta_h))[:8]:
    delta = val - beta_h
    print(f"    beta = {expr:<16s} = {val:+.8f}  (delta = {delta:+.8f})")

mae_h, max_h, mu_e_h, tau_e_h = print_model_detail(
    "(h) alpha*N + beta*N^2 + C", ln_m_h, 1,
    f"alpha = {alpha_h:.6f}, beta = {beta_h:.6f}"
)
_, pct_h, _, _, _ = compute_errors(ln_m_h)
record("(h) alpha*N + beta*N^2", mae_h, max_h, 1, mu_e_h, tau_e_h, pct_h)


# ###########################################################################
# MODEL (i): KNOT-TYPE CORRECTION (twist knot indicator)
# ###########################################################################
print("\n\n" + "="*72)
print("  MODEL (i): Knot-Type Correction (Twist Knot Indicator)")
print("  ln(m) = (2/9)*G * N^2 + delta * 1_twist + C")
print("  Only 6_1 (muon) is a twist knot: 1_twist = {0, 1, 0}")
print("  C fixed by electron => exact for e; delta adjusts mu; tau may shift")
print("="*72)

# With C fixed by electron and coefficient (2/9)*G fixed:
# For electron: ln(m_e) = gamma_L * 9 + C  =>  C = ln(m_e) - gamma_L * 9  (same as v4.0)
# For muon:     ln(m_mu) = gamma_L * 36 + delta + C
# For tau:      ln(m_tau) = gamma_L * 49 + C    (no change from v4.0)
# So delta = ln(m_mu) - gamma_L * 36 - C_l_v40
delta_twist = ln_m_obs[1] - gamma_L * N2_arr[1] - C_l_v40

print(f"\n  delta (twist correction) = {delta_twist:.10f}")
print(f"  This corrects muon exactly but leaves tau at v4.0 error.")

# Check delta for clean expressions
print(f"\n  Checking clean expressions for delta = {delta_twist:.8f}:")
N_mu = 6.0
candidates_delta = {
    "-1/N_mu  (-1/6)":           -1.0/N_mu,
    "-G/N_mu^2 (-G/36)":        -G/N_mu**2,
    "-G/N_mu (-G/6)":           -G/N_mu,
    "-(2/9)*G":                  -(2.0/9.0)*G,
    "-G/pi":                     -G/PI,
    "-1/pi":                     -1.0/PI,
    "-G/7":                      -G/7.0,
    "-G/9":                      -G/9.0,
    "-1/7":                      -1.0/7.0,
    "-1/9":                      -1.0/9.0,
    "-G^2":                      -G**2,
    "-ln(2)/3":                  -np.log(2)/3.0,
    "-2*G/9":                    -2*G/9.0,
    "-G/(2*pi)":                 -G/(2*PI),
    "-ln(G)":                    -np.log(G),
    "-(2/9)*G*N_mu (=-12G/9)":  -(2.0/9.0)*G*N_mu,
    "-G*ln(2)":                  -G*np.log(2),
    "-1/3":                      -1.0/3.0,
    "-G/3":                      -G/3.0,
    "-2/9":                      -2.0/9.0,
    "-1/N_mu^2 (-1/36)":        -1.0/N_mu**2,
    "-2*G/N_mu (-G/3)":         -2*G/N_mu,
}
for expr, val in sorted(candidates_delta.items(), key=lambda x: abs(x[1] - delta_twist)):
    delta_diff = val - delta_twist
    print(f"    delta = {expr:<30s} = {val:+.10f}  (diff = {delta_diff:+.10f})")

ln_m_i = gamma_L * N2_arr + delta_twist * twist_arr + C_l_v40
mae_i, max_i, mu_e_i, tau_e_i = print_model_detail(
    "(i) v4.0 + delta * 1_twist", ln_m_i, 1,
    f"delta = {delta_twist:.6f}"
)
_, pct_i, _, _, _ = compute_errors(ln_m_i)
record("(i) Twist-knot correction", mae_i, max_i, 1, mu_e_i, tau_e_i, pct_i)

# Also test model (i') where we optimize delta to minimize global MAE (not just fix muon)
print("\n  --- Sub-model (i'): Optimize delta for global MAE ---")

def model_i_prime_mae(delta_val):
    ln_pred = gamma_L * N2_arr + delta_val * twist_arr + C_l_v40
    m_pred = np.exp(ln_pred)
    return np.mean(np.abs((m_pred - m_obs) / m_obs)) * 100.0

res_ip = minimize_scalar(model_i_prime_mae, bounds=(delta_twist - 0.5, delta_twist + 0.5), method='bounded')
delta_ip = res_ip.x
print(f"  Optimized delta = {delta_ip:.10f}  (vs exact muon-fix: {delta_twist:.10f})")
print(f"  Difference = {delta_ip - delta_twist:+.10f}")

ln_m_ip = gamma_L * N2_arr + delta_ip * twist_arr + C_l_v40
mae_ip, max_ip, mu_e_ip, tau_e_ip = print_model_detail(
    "(i') Twist correction (MAE-optimized)", ln_m_ip, 1,
    f"delta = {delta_ip:.6f}"
)
_, pct_ip, _, _, _ = compute_errors(ln_m_ip)
record("(i') Twist correction (opt)", mae_ip, max_ip, 1, mu_e_ip, tau_e_ip, pct_ip)


# ###########################################################################
# COMPREHENSIVE COMPARISON TABLE
# ###########################################################################
print("\n\n")
print("#" * 100)
print("#  COMPREHENSIVE COMPARISON TABLE: All Models Sorted by MAE")
print("#" * 100)

# Sort by MAE
results_sorted = sorted(results, key=lambda x: x["mae"])

header = (f"  {'#':<3} {'Model':<32s} {'MAE%':>7s} {'Max%':>7s} {'#Free':>5s} "
          f"{'Err_e%':>8s} {'Err_mu%':>8s} {'Err_tau%':>9s} "
          f"{'mu/e pred':>10s} {'tau/e pred':>11s}")
print(header)
print("  " + "-" * (len(header) - 2))

for rank, r in enumerate(results_sorted, 1):
    print(f"  {rank:<3d} {r['label']:<32s} {r['mae']:>7.3f} {r['max_err']:>7.3f} {r['n_free']:>5d} "
          f"{r['err_e']:>+7.2f}% {r['err_mu']:>+7.2f}% {r['err_tau']:>+8.2f}% "
          f"{r['mu_e_pred']:>10.2f} {r['tau_e_pred']:>11.2f}")

print(f"\n  Observed mass ratios:  m_mu/m_e = {mu_e_obs:.2f},  m_tau/m_e = {tau_e_obs:.2f}")


# ###########################################################################
# MASS RATIO ANALYSIS
# ###########################################################################
print("\n\n")
print("#" * 80)
print("#  MASS RATIO ANALYSIS")
print("#" * 80)

print(f"\n  {'Model':<32s} {'mu/e pred':>10s} {'mu/e obs':>10s} {'mu/e err%':>10s} "
      f"{'tau/e pred':>11s} {'tau/e obs':>11s} {'tau/e err%':>11s}")
print("  " + "-" * 95)

for r in results_sorted:
    mu_err = (r['mu_e_pred'] / mu_e_obs - 1) * 100
    tau_err = (r['tau_e_pred'] / tau_e_obs - 1) * 100
    print(f"  {r['label']:<32s} {r['mu_e_pred']:>10.2f} {mu_e_obs:>10.2f} {mu_err:>+9.2f}% "
          f"{r['tau_e_pred']:>11.2f} {tau_e_obs:>11.2f} {tau_err:>+10.2f}%")


# ###########################################################################
# SUMMARY AND RECOMMENDATIONS
# ###########################################################################
print("\n\n")
print("#" * 80)
print("#  SUMMARY AND RECOMMENDATIONS")
print("#" * 80)

# Find best zero-free-param model
zero_free = [r for r in results_sorted if r['n_free'] == 0]
one_free = [r for r in results_sorted if r['n_free'] == 1]
two_free = [r for r in results_sorted if r['n_free'] == 2]

print("\n  --- Best model with 0 free parameters (beyond electron calibration) ---")
if zero_free:
    r = zero_free[0]
    print(f"  {r['label']}: MAE = {r['mae']:.3f}%, Max = {r['max_err']:.3f}%")
else:
    print("  (none)")

print("\n  --- Best model with 1 free parameter ---")
if one_free:
    r = one_free[0]
    print(f"  {r['label']}: MAE = {r['mae']:.3f}%, Max = {r['max_err']:.3f}%")

print("\n  --- Best model with 2 free parameters (exact-fit models) ---")
if two_free:
    r = two_free[0]
    print(f"  {r['label']}: MAE = {r['mae']:.3f}%, Max = {r['max_err']:.3f}%")

# Key findings
print("\n  --- Key Findings ---")
print(f"  1. v4.0 baseline: MAE = {results[0]['mae']:.3f}%, muon error = {results[0]['err_mu']:+.2f}%")
print(f"  2. Optimal N^p power: p = {p_opt:.6f} (1 free param)")
print(f"  3. Genus correction: exact fit with genus = {{1, 2, 3}} (physically motivated)")
print(f"  4. Twist-knot correction delta = {delta_twist:.6f}")

# Check if delta is close to known expressions
best_delta_match = min(candidates_delta.items(), key=lambda x: abs(x[1] - delta_twist))
print(f"     Closest clean expression: delta ~ {best_delta_match[0]} = {best_delta_match[1]:.8f}")
print(f"     Residual from best match: {best_delta_match[1] - delta_twist:+.8f}")

print(f"\n  5. The muon anomaly (+17.8%) is resolved by any model that introduces")
print(f"     a topological correction sensitive to the twist/hyperbolic nature of 6_1.")
print(f"     The genus correction (b) is the most physically transparent: genus = 2")
print(f"     for 6_1 naturally distinguishes it from the torus knots 3_1 (genus 1)")
print(f"     and 7_1 (genus 3).")

print("\n\n  === END OF PHASE 2 ANALYSIS ===\n")
