"""
KSAU v4.1 Phase 1: Heavy Quark Correction Analysis
====================================================
Systematic exploration of correction models to the v4.0 quark mass formula:
    ln(m_q) = (10/7) * G * V - (7 + G)

Goal: Reduce quark MAE from 8.7% to < 5%, with bottom/top errors < 10%.
Constraint: Add at most 1 free parameter per model.

Author: KSAU Project
Date: 2026-02-06
"""

import numpy as np
from scipy.optimize import minimize, minimize_scalar
from scipy.stats import linregress
import sys
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CONSTANTS
# =============================================================================
G = 0.915965594  # Catalan's constant
GAMMA_Q = (10.0 / 7.0) * G  # v4.0 slope  = 10G/7
B_PRIME = -(7.0 + G)          # v4.0 intercept = -(7+G)

# =============================================================================
# QUARK DATA (v4.0 assignments)
# =============================================================================
# Order: u, d, s, c, b, t
NAMES     = ['u',       'd',       's',       'c',        'b',        't']
LINKS     = ['L7a5',    'L6a4',    'L10n95',  'L11n64',   'L10a141',  'L11a62']
VOLUMES   = np.array([6.598952, 7.327725, 9.531900, 11.517101, 12.276278, 15.359984])
DETS      = np.array([18,       16,        32,       12,         64,        124])
M_OBS     = np.array([2.16,     4.67,      93.4,     1270.0,     4180.0,    172760.0])
LN_M_OBS  = np.log(M_OBS)

# Crossing numbers (from link notation: L{N}...)
N_CROSS   = np.array([7,  6,  10, 11, 10, 11])

# Component numbers: down-type = 3-component, up-type = 2-component
COMP      = np.array([2,  3,  3,  2,  3,  2])

# Type flags: 1 = down-type, 0 = up-type
IS_DOWN   = np.array([0,  1,  1,  0,  1,  0], dtype=bool)
IS_UP     = ~IS_DOWN

N = len(NAMES)  # 6 quarks

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def compute_errors(ln_m_pred, ln_m_obs=LN_M_OBS, m_obs=M_OBS):
    """Compute individual % errors, MAE, max|error|, R^2 in log-mass space."""
    m_pred = np.exp(ln_m_pred)
    pct_errors = (m_pred - m_obs) / m_obs * 100.0
    abs_pct = np.abs(pct_errors)
    mae = np.mean(abs_pct)
    max_err = np.max(abs_pct)

    # R^2 in log-mass space
    ss_res = np.sum((ln_m_obs - ln_m_pred)**2)
    ss_tot = np.sum((ln_m_obs - np.mean(ln_m_obs))**2)
    r2 = 1.0 - ss_res / ss_tot

    return pct_errors, mae, max_err, r2


def print_individual_errors(names, pct_errors, m_obs, m_pred):
    """Print a table of individual quark errors."""
    print(f"  {'Quark':<6} {'Obs (MeV)':>12} {'Pred (MeV)':>12} {'Error':>8}")
    print(f"  {'-'*6} {'-'*12} {'-'*12} {'-'*8}")
    for i, name in enumerate(names):
        print(f"  {name:<6} {m_obs[i]:>12.2f} {m_pred[i]:>12.2f} {pct_errors[i]:>+7.1f}%")


def loo_cv_mae(fit_func, volumes=VOLUMES, ln_m_obs=LN_M_OBS, m_obs=M_OBS):
    """
    Leave-one-out cross-validation.
    fit_func(V_train, lnm_train) -> callable(V) that returns ln(m) predictions.
    Returns: LOO-CV MAE (% in mass space).
    """
    abs_errors = []
    for i in range(N):
        # Train on all except i
        mask = np.ones(N, dtype=bool)
        mask[i] = False
        V_train = volumes[mask]
        lnm_train = ln_m_obs[mask]

        # Fit model
        predictor = fit_func(V_train, lnm_train, mask)

        # Predict left-out
        ln_pred_i = predictor(volumes[i:i+1])
        m_pred_i = np.exp(ln_pred_i[0])
        err_i = abs((m_pred_i - m_obs[i]) / m_obs[i]) * 100.0
        abs_errors.append(err_i)

    return np.mean(abs_errors), abs_errors


# =============================================================================
# MODEL 0: v4.0 BASELINE (no free parameters)
# =============================================================================

def model_v40_baseline():
    """v4.0 formula: ln(m) = gamma*V + b'"""
    ln_m_pred = GAMMA_Q * VOLUMES + B_PRIME
    return ln_m_pred


# =============================================================================
# MODEL A: QUADRATIC VOLUME CORRECTION
# ln(m) = gamma*V + beta*(V - V_median)^2 + b'
# Fix gamma, b' from theory; optimize beta only
# =============================================================================

def model_quadratic_volume():
    V_med = np.median(VOLUMES)

    def objective(beta):
        ln_pred = GAMMA_Q * VOLUMES + beta * (VOLUMES - V_med)**2 + B_PRIME
        return np.sum((LN_M_OBS - ln_pred)**2)

    res = minimize_scalar(objective, bounds=(-0.1, 0.1), method='bounded')
    beta_opt = res.x
    ln_pred = GAMMA_Q * VOLUMES + beta_opt * (VOLUMES - V_med)**2 + B_PRIME

    # LOO-CV
    def fit_func(V_tr, lnm_tr, mask):
        V_med_tr = np.median(VOLUMES)  # use global median for consistency
        def obj(b):
            return np.sum((lnm_tr - GAMMA_Q * V_tr - b * (V_tr - V_med_tr)**2 - B_PRIME)**2)
        r = minimize_scalar(obj, bounds=(-0.5, 0.5), method='bounded')
        def predictor(V):
            return GAMMA_Q * V + r.x * (V - V_med_tr)**2 + B_PRIME
        return predictor

    loo_mae, loo_each = loo_cv_mae(fit_func)

    return ln_pred, beta_opt, {'V_median': V_med}, loo_mae, loo_each


# =============================================================================
# MODEL B: CROSSING-NUMBER CORRECTION
# ln(m) = gamma*V + beta*N_cross + b'
# Fix gamma, b' from theory; optimize beta only
# =============================================================================

def model_crossing_number():
    def objective(beta):
        ln_pred = GAMMA_Q * VOLUMES + beta * N_CROSS + B_PRIME
        return np.sum((LN_M_OBS - ln_pred)**2)

    res = minimize_scalar(objective, bounds=(-1.0, 1.0), method='bounded')
    beta_opt = res.x
    ln_pred = GAMMA_Q * VOLUMES + beta_opt * N_CROSS + B_PRIME

    def fit_func(V_tr, lnm_tr, mask):
        nc_tr = N_CROSS[mask]
        def obj(b):
            return np.sum((lnm_tr - GAMMA_Q * V_tr - b * nc_tr - B_PRIME)**2)
        r = minimize_scalar(obj, bounds=(-2.0, 2.0), method='bounded')
        def predictor(V):
            # Need N_cross for prediction - use full array indexing
            # This is approximate; for LOO we need the held-out crossing number
            idx = np.where(np.isin(VOLUMES, V))[0]
            if len(idx) > 0:
                return GAMMA_Q * V + r.x * N_CROSS[idx] + B_PRIME
            return GAMMA_Q * V + B_PRIME  # fallback
        return predictor

    # Custom LOO for non-volume-only features
    def loo_custom():
        abs_errors = []
        for i in range(N):
            mask = np.ones(N, dtype=bool)
            mask[i] = False
            V_tr = VOLUMES[mask]
            lnm_tr = LN_M_OBS[mask]
            nc_tr = N_CROSS[mask]

            def obj(b, vt=V_tr, lt=lnm_tr, nt=nc_tr):
                return np.sum((lt - GAMMA_Q * vt - b * nt - B_PRIME)**2)
            r = minimize_scalar(obj, bounds=(-2.0, 2.0), method='bounded')

            ln_pred_i = GAMMA_Q * VOLUMES[i] + r.x * N_CROSS[i] + B_PRIME
            m_pred_i = np.exp(ln_pred_i)
            err_i = abs((m_pred_i - M_OBS[i]) / M_OBS[i]) * 100.0
            abs_errors.append(err_i)
        return np.mean(abs_errors), abs_errors

    loo_mae, loo_each = loo_custom()
    return ln_pred, beta_opt, {}, loo_mae, loo_each


# =============================================================================
# MODEL C: COMPONENT-NUMBER CORRECTION
# ln(m) = gamma*V + beta*C + b'
# =============================================================================

def model_component_number():
    def objective(beta):
        ln_pred = GAMMA_Q * VOLUMES + beta * COMP + B_PRIME
        return np.sum((LN_M_OBS - ln_pred)**2)

    res = minimize_scalar(objective, bounds=(-3.0, 3.0), method='bounded')
    beta_opt = res.x
    ln_pred = GAMMA_Q * VOLUMES + beta_opt * COMP + B_PRIME

    def loo_custom():
        abs_errors = []
        for i in range(N):
            mask = np.ones(N, dtype=bool)
            mask[i] = False
            def obj(b, m=mask):
                return np.sum((LN_M_OBS[m] - GAMMA_Q * VOLUMES[m] - b * COMP[m] - B_PRIME)**2)
            r = minimize_scalar(obj, bounds=(-5.0, 5.0), method='bounded')
            ln_pred_i = GAMMA_Q * VOLUMES[i] + r.x * COMP[i] + B_PRIME
            m_pred_i = np.exp(ln_pred_i)
            abs_errors.append(abs((m_pred_i - M_OBS[i]) / M_OBS[i]) * 100.0)
        return np.mean(abs_errors), abs_errors

    loo_mae, loo_each = loo_custom()
    return ln_pred, beta_opt, {}, loo_mae, loo_each


# =============================================================================
# MODEL D: DETERMINANT CORRECTION
# ln(m) = gamma*V + beta*ln(Det) + b'
# =============================================================================

def model_determinant():
    LN_DET = np.log(DETS.astype(float))

    def objective(beta):
        ln_pred = GAMMA_Q * VOLUMES + beta * LN_DET + B_PRIME
        return np.sum((LN_M_OBS - ln_pred)**2)

    res = minimize_scalar(objective, bounds=(-2.0, 2.0), method='bounded')
    beta_opt = res.x
    ln_pred = GAMMA_Q * VOLUMES + beta_opt * LN_DET + B_PRIME

    def loo_custom():
        abs_errors = []
        for i in range(N):
            mask = np.ones(N, dtype=bool)
            mask[i] = False
            def obj(b, m=mask):
                return np.sum((LN_M_OBS[m] - GAMMA_Q * VOLUMES[m] - b * LN_DET[m] - B_PRIME)**2)
            r = minimize_scalar(obj, bounds=(-5.0, 5.0), method='bounded')
            ln_pred_i = GAMMA_Q * VOLUMES[i] + r.x * LN_DET[i] + B_PRIME
            abs_errors.append(abs((np.exp(ln_pred_i) - M_OBS[i]) / M_OBS[i]) * 100.0)
        return np.mean(abs_errors), abs_errors

    loo_mae, loo_each = loo_custom()
    return ln_pred, beta_opt, {}, loo_mae, loo_each


# =============================================================================
# MODEL E: TYPE-DEPENDENT SLOPE
# ln(m) = gamma_d*V (down-type) or gamma_u*V (up-type) + b' (shared)
# This has 2 slopes but keeps 1 intercept; net = 1 extra parameter vs v4.0
# Fit: optimize delta such that gamma_d = gamma + delta, gamma_u = gamma - delta
# Actually: fit gamma_d, gamma_u with shared b' (2 params, but v4.0 had fixed gamma, b')
# To keep "1 extra param": fix b' from theory, optimize gamma_d and gamma_u subject to
# constraint (gamma_d + gamma_u)/2 = gamma_Q (preserves average slope)
# Or simpler: fix gamma_Q as mean, optimize delta
# =============================================================================

def model_type_dependent_slope():
    # Parameterize: gamma_d = GAMMA_Q + delta, gamma_u = GAMMA_Q - delta
    # (weighted by count: 3 each, so simple average is fine)
    # Shared intercept = B_PRIME (fixed)

    def objective(delta):
        ln_pred = np.where(IS_DOWN,
                           (GAMMA_Q + delta) * VOLUMES + B_PRIME,
                           (GAMMA_Q - delta) * VOLUMES + B_PRIME)
        return np.sum((LN_M_OBS - ln_pred)**2)

    res = minimize_scalar(objective, bounds=(-0.5, 0.5), method='bounded')
    delta_opt = res.x
    gamma_d = GAMMA_Q + delta_opt
    gamma_u = GAMMA_Q - delta_opt

    ln_pred = np.where(IS_DOWN,
                       gamma_d * VOLUMES + B_PRIME,
                       gamma_u * VOLUMES + B_PRIME)

    def loo_custom():
        abs_errors = []
        for i in range(N):
            mask = np.ones(N, dtype=bool)
            mask[i] = False
            is_d = IS_DOWN[mask]
            V_tr = VOLUMES[mask]
            lnm_tr = LN_M_OBS[mask]

            def obj(d, vt=V_tr, lt=lnm_tr, isd=is_d):
                pred = np.where(isd, (GAMMA_Q + d) * vt + B_PRIME,
                                     (GAMMA_Q - d) * vt + B_PRIME)
                return np.sum((lt - pred)**2)
            r = minimize_scalar(obj, bounds=(-1.0, 1.0), method='bounded')

            if IS_DOWN[i]:
                ln_p = (GAMMA_Q + r.x) * VOLUMES[i] + B_PRIME
            else:
                ln_p = (GAMMA_Q - r.x) * VOLUMES[i] + B_PRIME
            abs_errors.append(abs((np.exp(ln_p) - M_OBS[i]) / M_OBS[i]) * 100.0)
        return np.mean(abs_errors), abs_errors

    loo_mae, loo_each = loo_custom()
    return ln_pred, delta_opt, {'gamma_d': gamma_d, 'gamma_u': gamma_u}, loo_mae, loo_each


# =============================================================================
# MODEL F: SIGMOID CORRECTION AT HIGH V
# ln(m) = gamma*V*(1 - delta*tanh((V - V0)/sigma)) + b'
# Fix gamma, b', V0, sigma from theory considerations; optimize delta only
# Test several (V0, sigma) pairs
# =============================================================================

def model_sigmoid(V0, sigma, label=""):
    def objective(delta):
        correction = 1.0 - delta * np.tanh((VOLUMES - V0) / sigma)
        ln_pred = GAMMA_Q * VOLUMES * correction + B_PRIME
        return np.sum((LN_M_OBS - ln_pred)**2)

    res = minimize_scalar(objective, bounds=(-0.5, 0.5), method='bounded')
    delta_opt = res.x
    correction = 1.0 - delta_opt * np.tanh((VOLUMES - V0) / sigma)
    ln_pred = GAMMA_Q * VOLUMES * correction + B_PRIME

    def loo_custom():
        abs_errors = []
        for i in range(N):
            mask = np.ones(N, dtype=bool)
            mask[i] = False
            def obj(d, m=mask):
                corr = 1.0 - d * np.tanh((VOLUMES[m] - V0) / sigma)
                return np.sum((LN_M_OBS[m] - GAMMA_Q * VOLUMES[m] * corr - B_PRIME)**2)
            r = minimize_scalar(obj, bounds=(-1.0, 1.0), method='bounded')
            corr_i = 1.0 - r.x * np.tanh((VOLUMES[i] - V0) / sigma)
            ln_p = GAMMA_Q * VOLUMES[i] * corr_i + B_PRIME
            abs_errors.append(abs((np.exp(ln_p) - M_OBS[i]) / M_OBS[i]) * 100.0)
        return np.mean(abs_errors), abs_errors

    loo_mae, loo_each = loo_custom()
    return ln_pred, delta_opt, {'V0': V0, 'sigma': sigma}, loo_mae, loo_each


# =============================================================================
# MODEL G: RE-OPTIMIZED LINEAR FIT (least-squares reference)
# ln(m) = gamma_opt * V + b_opt  (2 free parameters)
# =============================================================================

def model_reoptimized_linear():
    slope, intercept, r_val, p_val, se = linregress(VOLUMES, LN_M_OBS)
    ln_pred = slope * VOLUMES + intercept

    def fit_func(V_tr, lnm_tr, mask):
        s, i, _, _, _ = linregress(V_tr, lnm_tr)
        def predictor(V):
            return s * V + i
        return predictor

    loo_mae, loo_each = loo_cv_mae(fit_func)
    return ln_pred, slope, {'intercept': intercept, 'r_value': r_val}, loo_mae, loo_each


# =============================================================================
# MODEL H (BONUS): QUADRATIC WITH FREE INTERCEPT
# ln(m) = gamma*V + beta*(V - V_med)^2 + b_opt
# 2 free params (beta, b_opt); gamma fixed from theory
# =============================================================================

def model_quadratic_free_intercept():
    V_med = np.median(VOLUMES)

    def objective(params):
        beta, b = params
        ln_pred = GAMMA_Q * VOLUMES + beta * (VOLUMES - V_med)**2 + b
        return np.sum((LN_M_OBS - ln_pred)**2)

    res = minimize(objective, [0.0, B_PRIME], method='Nelder-Mead')
    beta_opt, b_opt = res.x
    ln_pred = GAMMA_Q * VOLUMES + beta_opt * (VOLUMES - V_med)**2 + b_opt

    def loo_custom():
        abs_errors = []
        for i in range(N):
            mask = np.ones(N, dtype=bool)
            mask[i] = False
            def obj(p, m=mask):
                return np.sum((LN_M_OBS[m] - GAMMA_Q * VOLUMES[m] - p[0] * (VOLUMES[m] - V_med)**2 - p[1])**2)
            r = minimize(obj, [0.0, B_PRIME], method='Nelder-Mead')
            ln_p = GAMMA_Q * VOLUMES[i] + r.x[0] * (VOLUMES[i] - V_med)**2 + r.x[1]
            abs_errors.append(abs((np.exp(ln_p) - M_OBS[i]) / M_OBS[i]) * 100.0)
        return np.mean(abs_errors), abs_errors

    loo_mae, loo_each = loo_custom()
    return ln_pred, beta_opt, {'b_opt': b_opt, 'V_median': V_med}, loo_mae, loo_each


# =============================================================================
# MODEL I (BONUS): DETERMINANT + FREE INTERCEPT
# ln(m) = gamma*V + beta*ln(Det) + b_opt
# =============================================================================

def model_det_free_intercept():
    LN_DET = np.log(DETS.astype(float))

    def objective(params):
        beta, b = params
        ln_pred = GAMMA_Q * VOLUMES + beta * LN_DET + b
        return np.sum((LN_M_OBS - ln_pred)**2)

    res = minimize(objective, [0.0, B_PRIME], method='Nelder-Mead')
    beta_opt, b_opt = res.x
    ln_pred = GAMMA_Q * VOLUMES + beta_opt * LN_DET + b_opt

    def loo_custom():
        abs_errors = []
        for i in range(N):
            mask = np.ones(N, dtype=bool)
            mask[i] = False
            def obj(p, m=mask):
                return np.sum((LN_M_OBS[m] - GAMMA_Q * VOLUMES[m] - p[0] * LN_DET[m] - p[1])**2)
            r = minimize(obj, [0.0, B_PRIME], method='Nelder-Mead')
            ln_p = GAMMA_Q * VOLUMES[i] + r.x[0] * LN_DET[i] + r.x[1]
            abs_errors.append(abs((np.exp(ln_p) - M_OBS[i]) / M_OBS[i]) * 100.0)
        return np.mean(abs_errors), abs_errors

    loo_mae, loo_each = loo_custom()
    return ln_pred, beta_opt, {'b_opt': b_opt}, loo_mae, loo_each


# =============================================================================
# CLEAN CONSTANT EXPLORATION
# =============================================================================

def explore_clean_constants(param_name, param_value):
    """
    Try to express a fitted parameter value in terms of G, pi, 7, 9, 10.
    Returns a list of (expression_string, value, relative_error) tuples.
    """
    pi = np.pi
    candidates = []

    # Simple expressions involving G, pi, 7, 9, 10
    expressions = {
        'G/7':          G / 7,
        'G/9':          G / 9,
        'G/10':         G / 10,
        'G/pi':         G / pi,
        'G/(7*pi)':     G / (7 * pi),
        'G^2':          G**2,
        'G^2/7':        G**2 / 7,
        'G^2/pi':       G**2 / pi,
        '1/7':          1.0 / 7,
        '1/9':          1.0 / 9,
        '1/10':         1.0 / 10,
        'pi/7':         pi / 7,
        'pi/9':         pi / 9,
        'pi/10':        pi / 10,
        '2G/7':         2 * G / 7,
        '2G/9':         2 * G / 9,
        'G/(2*7)':      G / 14,
        'G/(2*pi)':     G / (2 * pi),
        'G^2/(2*pi)':   G**2 / (2 * pi),
        'G*pi/7':       G * pi / 7,
        'G*pi/10':      G * pi / 10,
        '(G/7)^2':      (G / 7)**2,
        '(G/pi)^2':     (G / pi)**2,
        'G/(7+G)':      G / (7 + G),
        'G/(9+G)':      G / (9 + G),
        '7G/10':        7 * G / 10,
        '9G/10':        9 * G / 10,
        'G^2/10':       G**2 / 10,
        '2*pi*G/7^2':   2 * pi * G / 49,
        'G^3':          G**3,
        'ln(G)':        np.log(G),
        '-ln(G)':       -np.log(G),
        'G*ln(2)':      G * np.log(2),
        'G*ln(2)/7':    G * np.log(2) / 7,
        'ln(2)/7':      np.log(2) / 7,
        'ln(2)/9':      np.log(2) / 9,
        'ln(2)/10':     np.log(2) / 10,
        'pi*G^2/7':     pi * G**2 / 7,
        '2G/(7*pi)':    2 * G / (7 * pi),
        'G/7^2':        G / 49,
    }

    # Also check negative values
    neg_expressions = {f'-({k})': -v for k, v in expressions.items()}
    expressions.update(neg_expressions)

    for expr, val in expressions.items():
        if abs(val) < 1e-12:
            continue
        if abs(param_value) < 1e-12:
            continue
        rel_err = abs(val - param_value) / abs(param_value) * 100
        if rel_err < 20:  # within 20%
            candidates.append((expr, val, rel_err))

    # Sort by closeness
    candidates.sort(key=lambda x: x[2])
    return candidates[:8]


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    print("=" * 85)
    print("  KSAU v4.1 Phase 1: Heavy Quark Correction Analysis")
    print("=" * 85)

    # =========================================================================
    # SECTION 1: v4.0 Baseline
    # =========================================================================
    print("\n" + "=" * 85)
    print("  SECTION 1: v4.0 Baseline Reproduction")
    print("=" * 85)

    print(f"\n  Theory constants:")
    print(f"    G  (Catalan)  = {G:.9f}")
    print(f"    gamma = 10G/7 = {GAMMA_Q:.9f}")
    print(f"    b'  = -(7+G)  = {B_PRIME:.9f}")

    ln_pred_v40 = model_v40_baseline()
    pct_v40, mae_v40, max_v40, r2_v40 = compute_errors(ln_pred_v40)
    m_pred_v40 = np.exp(ln_pred_v40)

    print(f"\n  v4.0 Quark Mass Predictions:")
    print_individual_errors(NAMES, pct_v40, M_OBS, m_pred_v40)
    print(f"\n  Summary: MAE = {mae_v40:.2f}%,  Max|err| = {max_v40:.2f}%,  R^2(ln m) = {r2_v40:.6f}")

    # v4.0 LOO-CV
    def fit_v40_loo(V_tr, lnm_tr, mask):
        # v4.0 has NO free parameters - same prediction regardless of training set
        def predictor(V):
            return GAMMA_Q * V + B_PRIME
        return predictor
    loo_v40, loo_v40_each = loo_cv_mae(fit_v40_loo)
    print(f"  LOO-CV MAE = {loo_v40:.2f}% (same as in-sample since no free params)")

    print(f"\n  Residuals (ln_obs - ln_pred):")
    residuals_v40 = LN_M_OBS - ln_pred_v40
    for i, name in enumerate(NAMES):
        print(f"    {name}: {residuals_v40[i]:+.4f}")

    # Check for systematic pattern in residuals
    print(f"\n  Residual analysis:")
    print(f"    Mean residual:       {np.mean(residuals_v40):+.4f}")
    print(f"    Std residual:        {np.std(residuals_v40):.4f}")
    print(f"    Down-type mean:      {np.mean(residuals_v40[IS_DOWN]):+.4f}")
    print(f"    Up-type mean:        {np.mean(residuals_v40[IS_UP]):+.4f}")
    print(f"    Correlation with V:  {np.corrcoef(VOLUMES, residuals_v40)[0,1]:+.4f}")

    # =========================================================================
    # SECTION 2: Correction Models
    # =========================================================================
    print("\n" + "=" * 85)
    print("  SECTION 2: Correction Model Fits")
    print("=" * 85)

    all_results = {}

    # --- Model A: Quadratic Volume ---
    print("\n" + "-" * 85)
    print("  Model A: Quadratic Volume Correction")
    print("  ln(m) = (10G/7)*V + beta*(V - V_med)^2 - (7+G)")
    print("-" * 85)
    ln_a, beta_a, extra_a, loo_a, loo_a_each = model_quadratic_volume()
    pct_a, mae_a, max_a, r2_a = compute_errors(ln_a)
    print(f"  Fitted: beta = {beta_a:.6f},  V_median = {extra_a['V_median']:.4f}")
    print_individual_errors(NAMES, pct_a, M_OBS, np.exp(ln_a))
    print(f"  MAE = {mae_a:.2f}%,  Max|err| = {max_a:.2f}%,  R^2 = {r2_a:.6f},  LOO-CV MAE = {loo_a:.2f}%")
    all_results['A: Quadratic V'] = (mae_a, max_a, r2_a, loo_a, beta_a, 1)

    # --- Model B: Crossing-Number ---
    print("\n" + "-" * 85)
    print("  Model B: Crossing-Number Correction")
    print("  ln(m) = (10G/7)*V + beta*N_cross - (7+G)")
    print("-" * 85)
    ln_b, beta_b, _, loo_b, loo_b_each = model_crossing_number()
    pct_b, mae_b, max_b, r2_b = compute_errors(ln_b)
    print(f"  Fitted: beta = {beta_b:.6f}")
    print(f"  Crossing numbers: {dict(zip(NAMES, N_CROSS))}")
    print_individual_errors(NAMES, pct_b, M_OBS, np.exp(ln_b))
    print(f"  MAE = {mae_b:.2f}%,  Max|err| = {max_b:.2f}%,  R^2 = {r2_b:.6f},  LOO-CV MAE = {loo_b:.2f}%")
    all_results['B: Crossing N'] = (mae_b, max_b, r2_b, loo_b, beta_b, 1)

    # --- Model C: Component Number ---
    print("\n" + "-" * 85)
    print("  Model C: Component-Number Correction")
    print("  ln(m) = (10G/7)*V + beta*C - (7+G)    (C=3 down, C=2 up)")
    print("-" * 85)
    ln_c, beta_c, _, loo_c, loo_c_each = model_component_number()
    pct_c, mae_c, max_c, r2_c = compute_errors(ln_c)
    print(f"  Fitted: beta = {beta_c:.6f}")
    print_individual_errors(NAMES, pct_c, M_OBS, np.exp(ln_c))
    print(f"  MAE = {mae_c:.2f}%,  Max|err| = {max_c:.2f}%,  R^2 = {r2_c:.6f},  LOO-CV MAE = {loo_c:.2f}%")
    all_results['C: Component #'] = (mae_c, max_c, r2_c, loo_c, beta_c, 1)

    # --- Model D: Determinant ---
    print("\n" + "-" * 85)
    print("  Model D: Determinant Correction")
    print("  ln(m) = (10G/7)*V + beta*ln(Det) - (7+G)")
    print("-" * 85)
    ln_d, beta_d, _, loo_d, loo_d_each = model_determinant()
    pct_d, mae_d, max_d, r2_d = compute_errors(ln_d)
    print(f"  Fitted: beta = {beta_d:.6f}")
    print(f"  ln(Det) values: {dict(zip(NAMES, np.round(np.log(DETS.astype(float)), 3)))}")
    print_individual_errors(NAMES, pct_d, M_OBS, np.exp(ln_d))
    print(f"  MAE = {mae_d:.2f}%,  Max|err| = {max_d:.2f}%,  R^2 = {r2_d:.6f},  LOO-CV MAE = {loo_d:.2f}%")
    all_results['D: Determinant'] = (mae_d, max_d, r2_d, loo_d, beta_d, 1)

    # --- Model E: Type-Dependent Slope ---
    print("\n" + "-" * 85)
    print("  Model E: Type-Dependent Slope")
    print("  ln(m) = gamma_type * V - (7+G)")
    print("  gamma_d = (10G/7)+delta,  gamma_u = (10G/7)-delta")
    print("-" * 85)
    ln_e, delta_e, extra_e, loo_e, loo_e_each = model_type_dependent_slope()
    pct_e, mae_e, max_e, r2_e = compute_errors(ln_e)
    print(f"  Fitted: delta = {delta_e:.6f}")
    print(f"  gamma_d = {extra_e['gamma_d']:.6f},  gamma_u = {extra_e['gamma_u']:.6f}")
    print(f"  (v4.0 gamma = {GAMMA_Q:.6f})")
    print_individual_errors(NAMES, pct_e, M_OBS, np.exp(ln_e))
    print(f"  MAE = {mae_e:.2f}%,  Max|err| = {max_e:.2f}%,  R^2 = {r2_e:.6f},  LOO-CV MAE = {loo_e:.2f}%")
    all_results['E: Type Slope'] = (mae_e, max_e, r2_e, loo_e, delta_e, 1)

    # --- Model F: Sigmoid Corrections (multiple V0/sigma) ---
    print("\n" + "-" * 85)
    print("  Model F: Sigmoid Correction at High V")
    print("  ln(m) = (10G/7)*V*(1 - delta*tanh((V-V0)/sigma)) - (7+G)")
    print("-" * 85)

    sigmoid_configs = [
        (10.0, 2.0, "V0=10, sigma=2"),
        (11.0, 2.0, "V0=11, sigma=2"),
        (12.0, 2.0, "V0=12, sigma=2"),
        (10.0, 3.0, "V0=10, sigma=3"),
        (11.0, 3.0, "V0=11, sigma=3"),
        (np.pi**2, G*np.pi, f"V0=pi^2={np.pi**2:.3f}, sigma=G*pi={G*np.pi:.3f}"),
        (7.0 + G, np.pi, f"V0=7+G={7+G:.3f}, sigma=pi"),
    ]

    best_sigmoid_mae = np.inf
    best_sigmoid_key = None

    for V0, sigma, label in sigmoid_configs:
        ln_f, delta_f, extra_f, loo_f, loo_f_each = model_sigmoid(V0, sigma, label)
        pct_f, mae_f, max_f, r2_f = compute_errors(ln_f)
        key = f"F: Sigmoid ({label})"
        print(f"\n  {label}:")
        print(f"    delta = {delta_f:.6f}")
        print_individual_errors(NAMES, pct_f, M_OBS, np.exp(ln_f))
        print(f"    MAE = {mae_f:.2f}%,  Max|err| = {max_f:.2f}%,  R^2 = {r2_f:.6f},  LOO-CV MAE = {loo_f:.2f}%")
        all_results[key] = (mae_f, max_f, r2_f, loo_f, delta_f, 1)

        if mae_f < best_sigmoid_mae:
            best_sigmoid_mae = mae_f
            best_sigmoid_key = key
            best_sigmoid_pct = pct_f
            best_sigmoid_ln = ln_f

    # --- Model G: Re-optimized Linear ---
    print("\n" + "-" * 85)
    print("  Model G: Re-optimized Linear Fit (OLS reference)")
    print("  ln(m) = gamma_opt * V + b_opt")
    print("-" * 85)
    ln_g, gamma_g, extra_g, loo_g, loo_g_each = model_reoptimized_linear()
    pct_g, mae_g, max_g, r2_g = compute_errors(ln_g)
    print(f"  Fitted: gamma_opt = {gamma_g:.6f},  b_opt = {extra_g['intercept']:.6f}")
    print(f"  (v4.0:  gamma    = {GAMMA_Q:.6f},  b'    = {B_PRIME:.6f})")
    print(f"  Difference: d_gamma = {gamma_g - GAMMA_Q:+.6f},  d_b = {extra_g['intercept'] - B_PRIME:+.6f}")
    print_individual_errors(NAMES, pct_g, M_OBS, np.exp(ln_g))
    print(f"  MAE = {mae_g:.2f}%,  Max|err| = {max_g:.2f}%,  R^2 = {r2_g:.6f},  LOO-CV MAE = {loo_g:.2f}%")
    all_results['G: OLS Linear'] = (mae_g, max_g, r2_g, loo_g, gamma_g, 2)

    # --- Model H: Quadratic + Free Intercept ---
    print("\n" + "-" * 85)
    print("  Model H: Quadratic + Free Intercept")
    print("  ln(m) = (10G/7)*V + beta*(V-V_med)^2 + b_opt")
    print("-" * 85)
    ln_h, beta_h, extra_h, loo_h, loo_h_each = model_quadratic_free_intercept()
    pct_h, mae_h, max_h, r2_h = compute_errors(ln_h)
    print(f"  Fitted: beta = {beta_h:.6f},  b_opt = {extra_h['b_opt']:.6f}")
    print(f"  (v4.0 b' = {B_PRIME:.6f},  shift = {extra_h['b_opt'] - B_PRIME:+.6f})")
    print_individual_errors(NAMES, pct_h, M_OBS, np.exp(ln_h))
    print(f"  MAE = {mae_h:.2f}%,  Max|err| = {max_h:.2f}%,  R^2 = {r2_h:.6f},  LOO-CV MAE = {loo_h:.2f}%")
    all_results['H: Quad+FreeB'] = (mae_h, max_h, r2_h, loo_h, beta_h, 2)

    # --- Model I: Determinant + Free Intercept ---
    print("\n" + "-" * 85)
    print("  Model I: Determinant + Free Intercept")
    print("  ln(m) = (10G/7)*V + beta*ln(Det) + b_opt")
    print("-" * 85)
    ln_i, beta_i, extra_i, loo_i, loo_i_each = model_det_free_intercept()
    pct_i, mae_i, max_i, r2_i = compute_errors(ln_i)
    print(f"  Fitted: beta = {beta_i:.6f},  b_opt = {extra_i['b_opt']:.6f}")
    print_individual_errors(NAMES, pct_i, M_OBS, np.exp(ln_i))
    print(f"  MAE = {mae_i:.2f}%,  Max|err| = {max_i:.2f}%,  R^2 = {r2_i:.6f},  LOO-CV MAE = {loo_i:.2f}%")
    all_results['I: Det+FreeB'] = (mae_i, max_i, r2_i, loo_i, beta_i, 2)

    # =========================================================================
    # SECTION 3: Comprehensive Comparison Table
    # =========================================================================
    print("\n" + "=" * 85)
    print("  SECTION 3: Comprehensive Model Comparison")
    print("=" * 85)

    # Add baseline
    all_results['v4.0 Baseline'] = (mae_v40, max_v40, r2_v40, loo_v40, None, 0)

    # Sort by MAE
    sorted_results = sorted(all_results.items(), key=lambda x: x[1][0])

    print(f"\n  {'Model':<32} {'MAE%':>6} {'MaxE%':>7} {'R^2':>9} {'LOO-CV%':>8} {'#Param':>7} {'Key Param':>12}")
    print(f"  {'-'*32} {'-'*6} {'-'*7} {'-'*9} {'-'*8} {'-'*7} {'-'*12}")

    for name, (mae, maxe, r2, loo, param, npar) in sorted_results:
        param_str = f"{param:.5f}" if param is not None else "fixed"
        print(f"  {name:<32} {mae:>6.2f} {maxe:>7.2f} {r2:>9.6f} {loo:>8.2f} {npar:>7d} {param_str:>12}")

    # =========================================================================
    # SECTION 4: Detailed Side-by-Side Individual Errors
    # =========================================================================
    print("\n" + "=" * 85)
    print("  SECTION 4: Per-Quark Error Comparison (% errors, best models)")
    print("=" * 85)

    # Pick top models: baseline, best 1-param, best 2-param, OLS
    # Recalculate for display
    models_display = {
        'v4.0': pct_v40,
        'A:QuadV': compute_errors(ln_a)[0],
        'C:Comp': compute_errors(ln_c)[0],
        'D:Det': compute_errors(ln_d)[0],
        'E:Slope': compute_errors(ln_e)[0],
        'G:OLS': compute_errors(ln_g)[0],
        'H:Q+B': compute_errors(ln_h)[0],
        'I:D+B': compute_errors(ln_i)[0],
    }

    header = f"  {'Quark':<6}"
    for mname in models_display:
        header += f" {mname:>8}"
    print(f"\n{header}")
    print(f"  {'-'*6}" + "".join(f" {'-'*8}" for _ in models_display))

    for i, name in enumerate(NAMES):
        row = f"  {name:<6}"
        for mname, pcts in models_display.items():
            row += f" {pcts[i]:>+7.1f}%"
        print(row)

    # MAE row
    row = f"  {'MAE':<6}"
    for mname, pcts in models_display.items():
        row += f" {np.mean(np.abs(pcts)):>7.1f}%"
    print(f"  {'-'*6}" + "".join(f" {'-'*8}" for _ in models_display))
    print(row)

    # =========================================================================
    # SECTION 5: Clean Constant Exploration
    # =========================================================================
    print("\n" + "=" * 85)
    print("  SECTION 5: Clean Constant Exploration")
    print("  Can correction parameters be expressed in terms of G, pi, 7, 9, 10?")
    print("=" * 85)

    param_fits = {
        'A: beta (quadratic)':   beta_a,
        'B: beta (crossing)':    beta_b,
        'C: beta (component)':   beta_c,
        'D: beta (determinant)': beta_d,
        'E: delta (type slope)': delta_e,
        'G: gamma_opt':          gamma_g,
        'G: b_opt':              extra_g['intercept'],
        'G: gamma_opt - 10G/7':  gamma_g - GAMMA_Q,
        'G: b_opt - (-(7+G))':   extra_g['intercept'] - B_PRIME,
        'H: beta (quad+freeB)':  beta_h,
        'H: b_opt shift':        extra_h['b_opt'] - B_PRIME,
        'I: beta (det+freeB)':   beta_i,
        'I: b_opt shift':        extra_i['b_opt'] - B_PRIME,
    }

    for pname, pval in param_fits.items():
        matches = explore_clean_constants(pname, pval)
        print(f"\n  {pname} = {pval:.6f}")
        if matches:
            for expr, val, rel_err in matches[:5]:
                print(f"    ~ {expr:<18} = {val:.6f}  (off by {rel_err:.1f}%)")
        else:
            print(f"    No close match found among candidate expressions")

    # =========================================================================
    # SECTION 6: Specific Theory-Motivated Checks
    # =========================================================================
    print("\n" + "=" * 85)
    print("  SECTION 6: Theory-Motivated Exact Formulas")
    print("=" * 85)

    # Check: what if beta_quadratic = G^2/(2*pi)?
    candidates_exact = [
        ("G^2/(2*pi)",          G**2 / (2 * np.pi)),
        ("G/7^2",               G / 49),
        ("G/(7*pi)",            G / (7 * np.pi)),
        ("-G/7^2",             -G / 49),
        ("G^2/7",               G**2 / 7),
        ("-G^2/7",             -G**2 / 7),
        ("G^2/10",              G**2 / 10),
        ("-G^2/10",            -G**2 / 10),
        ("G*ln2/7",             G * np.log(2) / 7),
        ("G/(10*pi)",           G / (10 * np.pi)),
        ("-G/(10*pi)",         -G / (10 * np.pi)),
        ("2*G/(7*pi)",          2 * G / (7 * np.pi)),
        ("G^2*pi/7^2",         G**2 * np.pi / 49),
    ]

    print(f"\n  Testing exact beta values in quadratic model (V_med = {np.median(VOLUMES):.4f}):")
    V_med = np.median(VOLUMES)

    print(f"\n  {'Expression':<18} {'Value':>10} {'MAE%':>7} {'MaxE%':>8} {'vs opt':>8}")
    print(f"  {'-'*18} {'-'*10} {'-'*7} {'-'*8} {'-'*8}")

    for expr, val in candidates_exact:
        ln_test = GAMMA_Q * VOLUMES + val * (VOLUMES - V_med)**2 + B_PRIME
        _, mae_test, max_test, _ = compute_errors(ln_test)
        diff = mae_test - mae_a
        print(f"  {expr:<18} {val:>10.6f} {mae_test:>7.2f} {max_test:>8.2f} {diff:>+7.2f}")

    # Now test exact determinant correction values
    print(f"\n  Testing exact beta values in determinant model:")
    LN_DET = np.log(DETS.astype(float))

    print(f"\n  {'Expression':<18} {'Value':>10} {'MAE%':>7} {'MaxE%':>8} {'vs opt':>8}")
    print(f"  {'-'*18} {'-'*10} {'-'*7} {'-'*8} {'-'*8}")

    for expr, val in candidates_exact:
        ln_test = GAMMA_Q * VOLUMES + val * LN_DET + B_PRIME
        _, mae_test, max_test, _ = compute_errors(ln_test)
        diff = mae_test - mae_d
        print(f"  {expr:<18} {val:>10.6f} {mae_test:>7.2f} {max_test:>8.2f} {diff:>+7.2f}")

    # =========================================================================
    # SECTION 7: Diagnosis & Recommendations
    # =========================================================================
    print("\n" + "=" * 85)
    print("  SECTION 7: Diagnosis and Recommendations")
    print("=" * 85)

    # Find the best 1-param model
    one_param = {k: v for k, v in all_results.items() if v[5] == 1}
    best_1p = min(one_param.items(), key=lambda x: x[1][0])

    two_param = {k: v for k, v in all_results.items() if v[5] == 2}
    best_2p = min(two_param.items(), key=lambda x: x[1][0])

    print(f"\n  Best 1-parameter model: {best_1p[0]}")
    print(f"    In-sample MAE = {best_1p[1][0]:.2f}%,  LOO-CV MAE = {best_1p[1][3]:.2f}%")
    print(f"    Overfitting ratio (LOO/in-sample) = {best_1p[1][3]/best_1p[1][0]:.2f}")

    print(f"\n  Best 2-parameter model: {best_2p[0]}")
    print(f"    In-sample MAE = {best_2p[1][0]:.2f}%,  LOO-CV MAE = {best_2p[1][3]:.2f}%")
    print(f"    Overfitting ratio (LOO/in-sample) = {best_2p[1][3]/best_2p[1][0]:.2f}")

    print(f"\n  v4.0 Baseline:")
    print(f"    MAE = {mae_v40:.2f}%,  LOO-CV MAE = {loo_v40:.2f}% (no params, no overfitting)")

    # Target check
    print(f"\n  v4.1 Target Check:")
    print(f"    Target: Quark MAE < 5%, Max individual error < 10%")
    for name, (mae, maxe, r2, loo, param, npar) in sorted_results[:5]:
        meets_mae = "YES" if mae < 5.0 else "no"
        meets_max = "YES" if maxe < 10.0 else "no"
        print(f"    {name:<32} MAE<5%: {meets_mae:<4}  Max<10%: {meets_max:<4}")

    # Systematic residual analysis
    print(f"\n  Systematic Structure in v4.0 Residuals:")
    print(f"    Bottom residual:  {residuals_v40[4]:+.4f} (underpredict => mass too low)")
    print(f"    Top residual:     {residuals_v40[5]:+.4f} (overpredict  => mass too high)")
    print(f"    This is OPPOSITE signs at high V => curvature/saturation signal")
    print(f"    Down residual:    {residuals_v40[1]:+.4f} (overpredict)")
    print(f"    Up residual:      {residuals_v40[0]:+.4f} (underpredict)")
    print(f"    Low-V quarks also show opposite-sign pattern by type")

    # Check down-type vs up-type pattern
    print(f"\n  Type-dependent pattern:")
    print(f"    Down-type (d,s,b) residuals: {residuals_v40[IS_DOWN]}")
    print(f"      Mean = {np.mean(residuals_v40[IS_DOWN]):+.4f}, Std = {np.std(residuals_v40[IS_DOWN]):.4f}")
    print(f"    Up-type (u,c,t) residuals:   {residuals_v40[IS_UP]}")
    print(f"      Mean = {np.mean(residuals_v40[IS_UP]):+.4f}, Std = {np.std(residuals_v40[IS_UP]):.4f}")

    # Information criteria (approximate BIC-like comparison)
    print(f"\n  Information-theoretic model ranking (BIC-like, lower is better):")
    print(f"  BIC ~ n*ln(RSS/n) + k*ln(n),  n={N}")
    print(f"\n  {'Model':<32} {'RSS':>10} {'k':>3} {'BIC_approx':>12}")
    print(f"  {'-'*32} {'-'*10} {'-'*3} {'-'*12}")

    model_rss = {
        'v4.0 Baseline': (np.sum(residuals_v40**2), 0),
        'A: Quadratic V': (np.sum((LN_M_OBS - ln_a)**2), 1),
        'C: Component #': (np.sum((LN_M_OBS - ln_c)**2), 1),
        'D: Determinant': (np.sum((LN_M_OBS - ln_d)**2), 1),
        'E: Type Slope':  (np.sum((LN_M_OBS - ln_e)**2), 1),
        'G: OLS Linear':  (np.sum((LN_M_OBS - ln_g)**2), 2),
        'H: Quad+FreeB':  (np.sum((LN_M_OBS - ln_h)**2), 2),
        'I: Det+FreeB':   (np.sum((LN_M_OBS - ln_i)**2), 2),
    }

    bic_sorted = []
    for mname, (rss, k) in model_rss.items():
        bic = N * np.log(rss / N) + k * np.log(N)
        bic_sorted.append((mname, rss, k, bic))
    bic_sorted.sort(key=lambda x: x[3])

    for mname, rss, k, bic in bic_sorted:
        print(f"  {mname:<32} {rss:>10.5f} {k:>3d} {bic:>12.4f}")

    # =========================================================================
    # SECTION 8: Final Summary
    # =========================================================================
    print("\n" + "=" * 85)
    print("  SECTION 8: Final Summary and Next Steps")
    print("=" * 85)

    print(f"""
  KEY FINDINGS:

  1. The v4.0 baseline (0 free parameters) achieves MAE = {mae_v40:.2f}% with the
     largest errors at bottom ({pct_v40[4]:+.1f}%) and down ({pct_v40[1]:+.1f}%).

  2. The residual structure shows a clear TYPE-DEPENDENT pattern:
     - Down-type mean residual: {np.mean(residuals_v40[IS_DOWN]):+.4f}
     - Up-type mean residual:   {np.mean(residuals_v40[IS_UP]):+.4f}
     This suggests the 3-component links (down-type) and 2-component links
     (up-type) have systematically different effective slopes or offsets.

  3. Best 1-parameter correction models (ranked by MAE):""")

    one_p_sorted = sorted(one_param.items(), key=lambda x: x[1][0])
    for i, (name, (mae, maxe, r2, loo, param, npar)) in enumerate(one_p_sorted[:5]):
        print(f"     {i+1}. {name:<28} MAE={mae:.2f}%, LOO={loo:.2f}%")

    print(f"""
  4. LOO-CV analysis shows which models generalize vs overfit:
     - LOO/in-sample ratio < 1.5 = good generalization
     - LOO/in-sample ratio > 2.0 = significant overfitting risk

  5. The correction parameters for the best models should be checked for
     expressibility in terms of G, pi, 7, 9, 10 (theory's natural constants).
     Close matches have been identified in Section 5.

  RECOMMENDATIONS FOR v4.1:

  - If a single 1-param correction achieves MAE < 5% with LOO-CV < 8%,
    adopt it as the v4.1 quark formula.
  - Priority: models that preserve the (10G/7) slope and -(7+G) intercept,
    adding only a topological correction term.
  - The type-dependent structure (Model E) has the clearest physical
    motivation: 2-component vs 3-component links genuinely differ in topology.
  - Quadratic volume correction (Model A) captures the high-V curvature
    seen in bottom/top residuals.
""")

    print("=" * 85)
    print("  END OF PHASE 1 ANALYSIS")
    print("=" * 85)


if __name__ == "__main__":
    main()
