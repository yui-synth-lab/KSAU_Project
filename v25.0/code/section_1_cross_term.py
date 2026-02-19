#!/usr/bin/env python3
"""
KSAU v25.0 Section 1 — (k_eff, z) Cross-Term Scaling Model
===========================================================
Model: R₀(k_eff, z) = A × k_eff^(-γ) × (1+z)^(β₀ + δβ × ln k_eff)

Four parameters: A, γ, β₀, δβ
Baseline (v24.0 Session 5): Single shared r0 per fold, β fixed at β_SSoT=13/6
                             LOO-CV MAE = 1.030σ (DES +1.82σ, KiDS −1.58σ)

Physical interpretation:
  r0(k) = A × k^(-γ)           — the z=0 coherence radius (survey-specific via k_eff)
  β(k)  = β₀ + δβ × ln(k)     — z-evolution rate (k_eff-dependent)
  r_z   = r0(k) × (1+z)^(-β(k)) — effective scale passed to the power spectrum engine

Auditor Requirements (per roadmap):
  1. Disclose 4 params / 5 data points → freedom ratio = 0.80 (high over-fitting risk)
  2. Report KiDS-included AND KiDS-excluded MAE separately
  3. AIC/BIC comparison with baseline (2-param Session 7 R-3 model)
  4. Negative result recorded honestly if MAE ≥ 1.030σ

Author: KSAU v25.0 Simulation Kernel — Section 1
Date:   2026-02-19
References: v24.0 Session 7, v25.0 Roadmap Section 1
"""

import sys, os, json, math
import numpy as np
from pathlib import Path
from scipy.optimize import minimize, curve_fit
from scipy.interpolate import RegularGridInterpolator

BASE = Path("E:/Obsidian/KSAU_Project")
sys.path.insert(0, str(BASE / "v23.0" / "code"))
from loo_cv_engine_v23_final_audit import LOOCVFinalAudit

CONFIG_PATH = str(BASE / "v23.0" / "data" / "cosmological_constants.json")
WL5_CONFIG  = str(BASE / "v25.0" / "data" / "wl5_survey_config.json")

# ─── SSoT Constants ──────────────────────────────────────────────────────────
KAPPA     = math.pi / 24         # 0.130900
ALPHA     = 1.0 / 48             # 0.020833
BETA_SSoT = 13.0 / 6.0           # 2.166667
R_BASE_SSoT = 3.0 / (2 * KAPPA)  # 11.459 Mpc/h

# ─── Session 5 LOO-CV R₀ baseline values (canonical) ────────────────────────
R0_LOO_S5 = {
    "DES Y3":      39.6295,
    "CFHTLenS":    29.5562,
    "DLS":         26.2132,
    "HSC Y3":      27.2116,
    "KiDS-Legacy": 19.6971,
}

# Session 5 baseline tensions (for comparison table)
S5_TENSIONS = {
    "DES Y3":      +1.821,
    "CFHTLenS":    +0.593,
    "DLS":         -0.877,
    "HSC Y3":      -0.279,
    "KiDS-Legacy": -1.580,
}

# ─── Load survey data ─────────────────────────────────────────────────────────
def load_surveys():
    with open(WL5_CONFIG, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    return cfg["surveys"]


# ─── Precompute S₈(r_z, z) grid ───────────────────────────────────────────────
def precompute_s8_grid(engine, z_vals, n_rz=80):
    """
    Precompute S₈ for a (r_z, z) grid to speed up optimization.

    Key insight: predict_s8_z(z, r0, beta) depends on r0 and beta
    only through r_z = r0 × (1+z)^(-beta). So S₈ is a 2D function
    of (r_z, z), not 3D. We exploit this to build a fast lookup table.
    """
    rz_grid = np.logspace(np.log10(2.0), np.log10(80.0), n_rz)
    s8_grid = np.zeros((n_rz, len(z_vals)))
    print(f"  Precomputing S₈ grid: {n_rz} × {len(z_vals)} = {n_rz*len(z_vals)} points...")
    for j, z in enumerate(z_vals):
        for i, rz in enumerate(rz_grid):
            # Pass r0=rz, beta=0 so r_z = rz × (1+z)^0 = rz
            s8_grid[i, j] = engine.predict_s8_z(z, rz, 0.0, use_nl=True)
    return rz_grid, s8_grid


def make_interpolator(rz_grid, z_vals, s8_grid):
    """Build a fast S₈(r_z, z) interpolator."""
    return RegularGridInterpolator(
        (np.log(rz_grid), np.array(z_vals)),
        s8_grid,
        method="linear",
        bounds_error=False,
        fill_value=None,
    )


def s8_interp(interp, rz, z):
    """Query the interpolated S₈ for given (r_z, z)."""
    rz_val = float(np.clip(rz, 2.0, 80.0))
    return float(interp([[np.log(rz_val), float(z)]])[0])


# ─── Cross-term model helpers ─────────────────────────────────────────────────
def compute_rz(k, z, A, gamma, beta0, dbeta):
    """Compute effective r_z for the cross-term model."""
    beta_eff = beta0 + dbeta * np.log(k)
    r0       = A * k ** (-gamma)
    return r0 * (1.0 + z) ** (-beta_eff)


def cross_term_cost(params, training_surveys, interp, z_idx):
    """χ² cost for cross-term model on training surveys."""
    A, gamma, beta0, dbeta = params
    if A <= 0 or gamma <= 0:
        return 1e9
    chi2 = 0.0
    for name, sv in training_surveys.items():
        k_j, z_j = sv["k_eff"], sv["z_eff"]
        rz_j = compute_rz(k_j, z_j, A, gamma, beta0, dbeta)
        if rz_j <= 0:
            return 1e9
        s8_pred_j = s8_interp(interp, rz_j, z_j)
        a_j = 1.0 / (1.0 + z_j)
        s8_obs_z_j  = sv["S8_obs"] * (a_j ** 0.55)
        s8_err_z_j  = sv["S8_err"] * (a_j ** 0.55)
        chi2 += ((s8_pred_j - s8_obs_z_j) / s8_err_z_j) ** 2
    return chi2


def fit_cross_term(training_surveys, interp, z_idx,
                   init=(10.0, 0.5, 2.0, 0.0)):
    """Optimize (A, γ, β₀, δβ) on training surveys."""
    best_res  = None
    best_cost = np.inf

    # Multiple restarts to avoid local minima
    inits = [
        init,
        (10.0, 0.5, 1.5, 0.5),
        (10.0, 0.5, 2.5, -0.5),
        (15.0, 0.4, 2.0, 0.0),
        (7.0,  0.5, 2.0, 1.0),
    ]
    for x0 in inits:
        res = minimize(
            cross_term_cost,
            x0,
            args=(training_surveys, interp, z_idx),
            method="Nelder-Mead",
            options={"xatol": 1e-5, "fatol": 1e-5, "maxiter": 5000},
        )
        if res.fun < best_cost:
            best_cost = res.fun
            best_res  = res

    return best_res.x, best_cost


# ─── Section 1a: Global cross-term fit ────────────────────────────────────────
def global_cross_term_fit(surveys, interp):
    """
    1a: Fit (A, γ, β₀, δβ) globally on all 5 surveys in S₈ space.
    This is the full-data fit (not LOO-CV), used for model characterisation.
    """
    params_opt, chi2_opt = fit_cross_term(surveys, interp, None)
    A, gamma, beta0, dbeta = params_opt

    per_survey = []
    for name, sv in surveys.items():
        k, z = sv["k_eff"], sv["z_eff"]
        rz   = compute_rz(k, z, A, gamma, beta0, dbeta)
        beta_eff = beta0 + dbeta * np.log(k)
        s8_pred = s8_interp(interp, rz, z)
        a = 1.0 / (1.0 + z)
        s8_obs_z = sv["S8_obs"] * (a ** 0.55)
        s8_err_z = sv["S8_err"] * (a ** 0.55)
        tension  = (s8_pred - s8_obs_z) / s8_err_z
        per_survey.append({
            "survey":   name,
            "k_eff":    k,
            "z_eff":    z,
            "beta_eff": round(beta_eff, 4),
            "r_z_pred": round(rz, 3),
            "s8_pred":  round(s8_pred, 4),
            "s8_obs_z": round(s8_obs_z, 4),
            "tension":  round(tension, 3),
        })

    return {
        "A": round(A, 4),
        "gamma": round(gamma, 4),
        "beta0": round(beta0, 4),
        "dbeta": round(dbeta, 4),
        "chi2":  round(chi2_opt, 4),
        "per_survey": per_survey,
    }


# ─── Section 1b: LOO-CV with cross-term model ─────────────────────────────────
def loo_cv_cross_term(surveys, interp):
    """
    1b: LOO-CV with the cross-term model.

    For each fold i:
      1. Fit (A, γ, β₀, δβ) on 4 training surveys
      2. Predict S₈ for held-out survey
      3. Compute tension

    AUDITOR NOTE: 4 params / 4 training data points per fold = complete determination.
    The training χ² will be near-zero (nearly perfect interpolation).
    The held-out survey prediction is extrapolation, not interpolation.
    """
    names   = list(surveys.keys())
    results = {}

    for held_out in names:
        train = {n: surveys[n] for n in names if n != held_out}

        # Fit cross-term model on 4 training surveys
        params_opt, train_chi2 = fit_cross_term(train, interp, None)
        A, gamma, beta0, dbeta = params_opt

        # Predict for held-out survey
        sv     = surveys[held_out]
        k_ho   = sv["k_eff"]
        z_ho   = sv["z_eff"]
        rz_ho  = compute_rz(k_ho, z_ho, A, gamma, beta0, dbeta)
        b_eff  = beta0 + dbeta * np.log(k_ho)
        s8_pred = s8_interp(interp, rz_ho, z_ho)
        a_ho   = 1.0 / (1.0 + z_ho)
        s8_obs_z  = sv["S8_obs"] * (a_ho ** 0.55)
        s8_err_z  = sv["S8_err"] * (a_ho ** 0.55)
        tension   = (s8_pred - s8_obs_z) / s8_err_z

        results[held_out] = {
            "A_loo":         round(A, 4),
            "gamma_loo":     round(gamma, 4),
            "beta0_loo":     round(beta0, 4),
            "dbeta_loo":     round(dbeta, 4),
            "beta_eff_ho":   round(b_eff, 4),
            "rz_pred_ho":    round(rz_ho, 3),
            "s8_pred":       round(s8_pred, 4),
            "s8_obs_z":      round(s8_obs_z, 4),
            "s8_err_z":      round(s8_err_z, 4),
            "tension":       round(tension, 4),
            "train_chi2":    round(train_chi2, 4),
        }

    tensions_all = [v["tension"] for v in results.values()]
    mae_all      = float(np.mean(np.abs(tensions_all)))
    n_lt15       = sum(1 for t in tensions_all if abs(t) < 1.5)
    n_lt10       = sum(1 for t in tensions_all if abs(t) < 1.0)

    # KiDS-excluded MAE
    tensions_excl_kids = [v["tension"] for k, v in results.items() if k != "KiDS-Legacy"]
    mae_excl_kids      = float(np.mean(np.abs(tensions_excl_kids)))

    return {
        "per_fold":       results,
        "mae_all":        round(mae_all, 4),
        "mae_excl_kids":  round(mae_excl_kids, 4),
        "n_lt15_sigma":   n_lt15,
        "n_lt10_sigma":   n_lt10,
        "n_surveys":      len(names),
        "n_params":       4,
        "dof_ratio":      round(4.0 / len(names), 2),
        "freedom_note":   "4 params / 5 data points = 0.80 (over-fitting risk: HIGH per auditor directive)",
    }


# ─── Section 1c: Two-regime β model ───────────────────────────────────────────
def two_regime_model_cost(params, surveys_list, interp):
    """χ² for two-regime β model."""
    A, gamma, beta_low, beta_high = params
    K_THRESH = 0.35
    if A <= 0 or gamma <= 0:
        return 1e9
    chi2 = 0.0
    for sv in surveys_list:
        k, z = sv["k_eff"], sv["z_eff"]
        beta_eff = beta_low if k <= K_THRESH else beta_high
        r0       = A * k ** (-gamma)
        rz       = r0 * (1.0 + z) ** (-beta_eff)
        if rz <= 0:
            return 1e9
        s8_pred = s8_interp(interp, rz, z)
        a       = 1.0 / (1.0 + z)
        s8_obs_z = sv["S8_obs"] * (a ** 0.55)
        s8_err_z = sv["S8_err"] * (a ** 0.55)
        chi2 += ((s8_pred - s8_obs_z) / s8_err_z) ** 2
    return chi2


def loo_cv_two_regime(surveys, interp):
    """LOO-CV for the two-regime β model (Section 1c)."""
    names  = list(surveys.keys())
    results = {}
    K_THRESH = 0.35

    for held_out in names:
        train_svs = [surveys[n] for n in names if n != held_out]

        res = minimize(
            two_regime_model_cost,
            [10.0, 0.5, 2.0, 1.5],
            args=(train_svs, interp),
            method="Nelder-Mead",
            options={"xatol": 1e-5, "fatol": 1e-5, "maxiter": 5000},
        )
        A, gamma, beta_low, beta_high = res.x

        sv      = surveys[held_out]
        k_ho, z_ho = sv["k_eff"], sv["z_eff"]
        beta_eff_ho = beta_low if k_ho <= K_THRESH else beta_high
        rz_ho   = A * k_ho ** (-gamma) * (1.0 + z_ho) ** (-beta_eff_ho)
        s8_pred = s8_interp(interp, rz_ho, z_ho)
        a_ho    = 1.0 / (1.0 + z_ho)
        s8_obs_z  = sv["S8_obs"] * (a_ho ** 0.55)
        s8_err_z  = sv["S8_err"] * (a_ho ** 0.55)
        tension   = (s8_pred - s8_obs_z) / s8_err_z

        results[held_out] = {
            "A_loo":       round(A, 4),
            "gamma_loo":   round(gamma, 4),
            "beta_low_loo":  round(beta_low, 4),
            "beta_high_loo": round(beta_high, 4),
            "regime":      "low" if k_ho <= K_THRESH else "high",
            "s8_pred":     round(s8_pred, 4),
            "s8_obs_z":    round(s8_obs_z, 4),
            "tension":     round(tension, 4),
        }

    tensions = [v["tension"] for v in results.values()]
    mae      = float(np.mean(np.abs(tensions)))
    return {
        "per_fold":      results,
        "mae_all":       round(mae, 4),
        "n_params":      4,
        "k_threshold":   K_THRESH,
        "note": "Two-regime β: beta_low for k≤0.35, beta_high for k>0.35",
    }


# ─── AIC / BIC model comparison ───────────────────────────────────────────────
def compute_aic_bic(surveys, interp):
    """
    Compute AIC and BIC for model comparison (using global full-data fit).

    Models compared:
      M0: Session 7 R-3 baseline    — A, γ only (β fixed=β_SSoT, δβ=0), 2 params
      M1: Cross-term                — A, γ, β₀, δβ, 4 params
      M2: Two-regime β              — A, γ, β_low, β_high, 4 params (k_thresh fixed)

    Note: n = 5 data points, fitting in S₈-tension space (Gaussian likelihood).
    AIC = 2k - 2ln(L) ≈ 2k + χ²_min   (for Gaussian, -2ln(L) = χ²)
    BIC = k ln(n) - 2ln(L) ≈ k ln(n) + χ²_min
    """
    n = 5

    # M0: baseline — 2 free params (A, γ), β fixed at β_SSoT
    def baseline_cost(params_2):
        A, gamma = params_2
        chi2 = 0.0
        for sv in surveys.values():
            k, z = sv["k_eff"], sv["z_eff"]
            rz   = A * k ** (-gamma) * (1.0 + z) ** (-BETA_SSoT)
            if rz <= 0:
                return 1e9
            s8_pred = s8_interp(interp, rz, z)
            a = 1.0 / (1.0 + z)
            s8_obs_z = sv["S8_obs"] * (a ** 0.55)
            s8_err_z = sv["S8_err"] * (a ** 0.55)
            chi2 += ((s8_pred - s8_obs_z) / s8_err_z) ** 2
        return chi2

    res_m0 = minimize(baseline_cost, [10.0, 0.5], method="Nelder-Mead",
                      options={"xatol": 1e-6, "fatol": 1e-6, "maxiter": 5000})
    chi2_m0 = float(res_m0.fun)
    k0 = 2

    # M1: cross-term — 4 free params
    chi2_m1 = cross_term_cost(
        fit_cross_term(surveys, interp, None)[0],
        surveys, interp, None,
    )
    k1 = 4

    # M2: two-regime β — 4 free params
    res_m2 = minimize(
        two_regime_model_cost, [10.0, 0.5, 2.0, 1.5],
        args=(list(surveys.values()), interp),
        method="Nelder-Mead",
        options={"xatol": 1e-6, "fatol": 1e-6, "maxiter": 5000},
    )
    chi2_m2 = float(res_m2.fun)
    k2 = 4

    def aic(k, chi2): return 2 * k + chi2
    def bic(k, chi2, n=5): return k * math.log(n) + chi2

    return {
        "n_data":   n,
        "note":     "AIC = 2k + χ²_min, BIC = k×ln(n) + χ²_min (Gaussian likelihood)",
        "M0_baseline": {
            "model":  "R₀ = A × k^(-γ) × (1+z)^β_SSoT (2 params, β fixed)",
            "k":      k0,
            "chi2":   round(chi2_m0, 4),
            "AIC":    round(aic(k0, chi2_m0), 4),
            "BIC":    round(bic(k0, chi2_m0), 4),
            "A_fit":  round(res_m0.x[0], 4),
            "gamma_fit": round(res_m0.x[1], 4),
        },
        "M1_cross_term": {
            "model":  "R₀ = A × k^(-γ) × (1+z)^(β₀+δβ ln k) (4 params)",
            "k":      k1,
            "chi2":   round(chi2_m1, 4),
            "AIC":    round(aic(k1, chi2_m1), 4),
            "BIC":    round(bic(k1, chi2_m1), 4),
        },
        "M2_two_regime": {
            "model":  "Two-regime β: β_low (k≤0.35) / β_high (k>0.35) (4 params)",
            "k":      k2,
            "chi2":   round(chi2_m2, 4),
            "AIC":    round(aic(k2, chi2_m2), 4),
            "BIC":    round(bic(k2, chi2_m2), 4),
        },
        "preferred_by_AIC": (
            "M0_baseline" if aic(k0, chi2_m0) <= min(aic(k1, chi2_m1), aic(k2, chi2_m2))
            else ("M1_cross_term" if aic(k1, chi2_m1) <= aic(k2, chi2_m2) else "M2_two_regime")
        ),
        "preferred_by_BIC": (
            "M0_baseline" if bic(k0, chi2_m0) <= min(bic(k1, chi2_m1), bic(k2, chi2_m2))
            else ("M1_cross_term" if bic(k1, chi2_m1) <= bic(k2, chi2_m2) else "M2_two_regime")
        ),
    }


# ─── Summary and criteria check ──────────────────────────────────────────────
def evaluate_success_criteria(loo_results):
    """Evaluate Section 1 success criteria."""
    mae = loo_results["mae_all"]
    folds = loo_results["per_fold"]
    des_t  = folds["DES Y3"]["tension"]
    kids_t = folds["KiDS-Legacy"]["tension"]

    # k_eff invariant CV: R₀ × k_eff^γ / (1+z)^β₀ should be constant
    # Use the global fit β0 and γ as proxy
    return {
        "target_1_mae_lt_08":   {"value": mae, "pass": mae < 0.8,
                                  "note": f"MAE={mae:.4f}σ (target <0.80σ)"},
        "target_2_mae_lt_10":   {"value": mae, "pass": mae < 1.0,
                                  "note": f"MAE={mae:.4f}σ (target <1.00σ, v25.0 MUST)"},
        "target_3_des_tension": {"value": abs(des_t), "pass": abs(des_t) < 1.5,
                                  "note": f"|DES tension|={abs(des_t):.4f}σ (target <1.5σ)"},
        "target_4_kids_tension":{"value": abs(kids_t), "pass": abs(kids_t) < 1.5,
                                  "note": f"|KiDS tension|={abs(kids_t):.4f}σ (target <1.5σ)"},
        "target_5_simultaneous":{"value": max(abs(des_t), abs(kids_t)),
                                  "pass": abs(des_t) < 1.5 and abs(kids_t) < 1.5,
                                  "note": "Both DES and KiDS |tension|<1.5σ simultaneously"},
        "v24_baseline_mae":     1.030,
        "improvement_vs_v24":   round(1.030 - mae, 4),
    }


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 76)
    print("KSAU v25.0 Section 1 — Cross-Term Scaling Model")
    print("Model: R₀(k,z) = A × k^(-γ) × (1+z)^(β₀ + δβ ln k)")
    print("=" * 76)
    print(f"\nSSoT: κ={KAPPA:.8f}, α={ALPHA:.8f}, β_SSoT={BETA_SSoT:.6f}")
    print(f"      R_base_SSoT = {R_BASE_SSoT:.4f} Mpc/h\n")

    # Load data
    surveys = load_surveys()
    engine  = LOOCVFinalAudit(config_path=CONFIG_PATH)
    z_vals  = sorted(set(s["z_eff"] for s in surveys.values()))
    print(f"Loaded {len(surveys)} surveys. z_eff values: {z_vals}")

    # Precompute S₈ grid
    print("\nStep 1: Precomputing S₈(r_z, z) grid...")
    rz_grid, s8_grid = precompute_s8_grid(engine, z_vals, n_rz=80)
    interp = make_interpolator(rz_grid, z_vals, s8_grid)
    print(f"  Done. r_z range: [{rz_grid[0]:.2f}, {rz_grid[-1]:.2f}] Mpc/h")

    # 1a: Global fit
    print("\nStep 2: Global cross-term fit (all 5 surveys)...")
    global_fit = global_cross_term_fit(surveys, interp)
    print(f"  A={global_fit['A']}, γ={global_fit['gamma']}, "
          f"β₀={global_fit['beta0']}, δβ={global_fit['dbeta']}")
    print(f"  χ² = {global_fit['chi2']}")
    for sv in global_fit["per_survey"]:
        print(f"    {sv['survey']:<14} β_eff={sv['beta_eff']:.3f}  "
              f"tension={sv['tension']:+.3f}σ")

    # 1b: LOO-CV
    print("\nStep 3: LOO-CV with cross-term model (BLOCKING — 5 folds)...")
    loo_results = loo_cv_cross_term(surveys, interp)
    print(f"  LOO-CV MAE (all 5) = {loo_results['mae_all']:.4f}σ")
    print(f"  LOO-CV MAE (excl KiDS) = {loo_results['mae_excl_kids']:.4f}σ")
    print(f"  n_lt1.5σ = {loo_results['n_lt15_sigma']}/5")
    print(f"\n  Per-fold tensions vs v24.0 Session 5 baseline:")
    print(f"  {'Survey':<14} {'v24.0':>8} {'v25.0':>8}  {'Δ':>8}  {'Pass<1.5':>10}")
    for name, fold in loo_results["per_fold"].items():
        v24t = S5_TENSIONS[name]
        v25t = fold["tension"]
        delta = v25t - v24t
        ok   = "✓" if abs(v25t) < 1.5 else "✗"
        print(f"  {name:<14} {v24t:>+8.3f}σ {v25t:>+8.3f}σ {delta:>+8.3f}σ {ok:>10}")

    # 1c: Two-regime model
    print("\nStep 4: Two-regime β model (Section 1c)...")
    two_regime = loo_cv_two_regime(surveys, interp)
    print(f"  Two-regime LOO-CV MAE = {two_regime['mae_all']:.4f}σ")

    # AIC/BIC
    print("\nStep 5: AIC/BIC model comparison...")
    aic_bic = compute_aic_bic(surveys, interp)
    print(f"  M0 (baseline, 2 params): χ²={aic_bic['M0_baseline']['chi2']:.4f}, "
          f"AIC={aic_bic['M0_baseline']['AIC']:.4f}, BIC={aic_bic['M0_baseline']['BIC']:.4f}")
    print(f"  M1 (cross-term, 4 params): χ²={aic_bic['M1_cross_term']['chi2']:.4f}, "
          f"AIC={aic_bic['M1_cross_term']['AIC']:.4f}, BIC={aic_bic['M1_cross_term']['BIC']:.4f}")
    print(f"  M2 (two-regime, 4 params): χ²={aic_bic['M2_two_regime']['chi2']:.4f}, "
          f"AIC={aic_bic['M2_two_regime']['AIC']:.4f}, BIC={aic_bic['M2_two_regime']['BIC']:.4f}")
    print(f"  Preferred by AIC: {aic_bic['preferred_by_AIC']}")
    print(f"  Preferred by BIC: {aic_bic['preferred_by_BIC']}")

    # Success criteria
    criteria = evaluate_success_criteria(loo_results)
    print("\n  Success criteria:")
    for key, val in criteria.items():
        if isinstance(val, dict):
            status = "PASS ✓" if val["pass"] else "FAIL ✗"
            print(f"    [{status}] {val['note']}")

    # Honest assessment
    improved = loo_results["mae_all"] < 1.030
    des_fixed  = abs(loo_results["per_fold"]["DES Y3"]["tension"]) < 1.5
    kids_fixed = abs(loo_results["per_fold"]["KiDS-Legacy"]["tension"]) < 1.5

    if not improved:
        print("\n  NEGATIVE RESULT: Cross-term model does NOT improve MAE vs v24.0 baseline.")
        print("  This confirms the v23.0 engine's structural limitation.")
        print("  The non-universal β issue persists beyond simple cross-term correction.")
    else:
        print(f"\n  POSITIVE RESULT: MAE improved from 1.030σ → {loo_results['mae_all']:.4f}σ.")

    # Build full results dict
    results = {
        "date":        "2026-02-19",
        "section":     "Section 1",
        "model":       "R₀(k,z) = A × k^(-γ) × (1+z)^(β₀ + δβ ln k)",
        "ssot": {
            "kappa":        KAPPA,
            "alpha":        ALPHA,
            "beta_ssot":    BETA_SSoT,
            "r_base_ssot":  R_BASE_SSoT,
        },
        "v24_baseline": {
            "mae_sigma":    1.030,
            "DES_tension":  +1.821,
            "KiDS_tension": -1.580,
        },
        "section_1a_global_fit":   global_fit,
        "section_1b_loo_cv":       loo_results,
        "section_1c_two_regime":   two_regime,
        "section_1_aic_bic":       aic_bic,
        "success_criteria":        criteria,
        "verdict": {
            "improved_mae":       improved,
            "des_tension_fixed":  des_fixed,
            "kids_tension_fixed": kids_fixed,
            "both_tensions_fixed": des_fixed and kids_fixed,
            "overfitting_warning": (
                "4 params / 5 data → dof_ratio = 0.80. "
                "Training χ² near-zero for each fold (near-complete determination). "
                "AIC/BIC penalise the 2-parameter increase vs baseline. "
                "Negative LOO-CV result indicates extrapolation fails despite training fit."
                if not improved else
                "4 params / 5 data → dof_ratio = 0.80. "
                "MAE improvement may reflect over-fitting. "
                "AIC/BIC comparison required to determine if additional parameters are justified."
            ),
        },
    }

    # Save results
    out_path = BASE / "v25.0" / "data" / "section_1_results.json"
    with open(str(out_path), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved → {out_path}")
    return results


if __name__ == "__main__":
    main()
