#!/usr/bin/env python3
"""
KSAU v25.0 Session 2 — Section 1 v2: Physical-Constraint LOO-CV + KiDS z_eff Variants
========================================================================================
Addresses ng.md BLOCKING issues:
  P2: Physical constraints in optimization (A>1.0, γ∈(0,2), β₀∈(-5,10), δβ∈(-10,10))
      + post-optimization sanity checks (r_z∈[2,80] Mpc/h, β_eff>0)
      + degenerate folds flagged and excluded from MAE
  P3: M0 baseline_cost() now enforces γ>0 (same pattern as cross_term_cost)
  P1: LOO-CV re-run with KiDS z_eff=0.526 (mean n(z)) and z_eff=0.482 (S8-weighted)
      Comparison table vs published z_eff=0.26

Author: KSAU v25.0 Session 2 — Simulation Kernel
Date:   2026-02-18 (Session 2)
References: v25.0 ng.md P1/P2/P3, v25.0 Roadmap Section 1
"""

import sys, os, json, math
import numpy as np
from pathlib import Path
from scipy.optimize import minimize

BASE = Path("E:/Obsidian/KSAU_Project")
sys.path.insert(0, str(BASE / "v23.0" / "code"))
from loo_cv_engine_v23_final_audit import LOOCVFinalAudit

CONFIG_PATH = str(BASE / "v23.0" / "data" / "cosmological_constants.json")
WL5_CONFIG  = str(BASE / "v25.0" / "data" / "wl5_survey_config.json")

# ─── SSoT Constants ──────────────────────────────────────────────────────────
KAPPA     = math.pi / 24
ALPHA     = 1.0 / 48
BETA_SSoT = 13.0 / 6.0
R_BASE_SSoT = 3.0 / (2 * KAPPA)

# v25.0 v1 LOO tensions (for comparison)
V1_TENSIONS = {
    "DES Y3":      1.7151,
    "CFHTLenS":    0.3293,
    "DLS":        -1.4566,
    "HSC Y3":      1.5367,
    "KiDS-Legacy":-3.0889,
}
V24_TENSIONS = {
    "DES Y3":     +1.821,
    "CFHTLenS":   +0.593,
    "DLS":        -0.877,
    "HSC Y3":     -0.279,
    "KiDS-Legacy":-1.580,
}

# Physical constraint bounds (P2 fix)
A_MIN, A_MAX        = 1.0,   200.0
GAMMA_MIN, GAMMA_MAX = 0.001, 2.0
BETA0_MIN, BETA0_MAX = -5.0,  10.0
DBETA_MIN, DBETA_MAX = -10.0, 10.0

# Sanity check bounds for r_z and beta_eff (P2 fix)
RZ_MIN, RZ_MAX   = 2.0, 80.0


# ─── Load survey data ─────────────────────────────────────────────────────────
def load_surveys():
    with open(WL5_CONFIG, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    return cfg["surveys"]


# ─── Precompute S₈(r_z, z) grid ───────────────────────────────────────────────
def precompute_s8_grid(engine, z_vals, n_rz=80):
    from scipy.interpolate import RegularGridInterpolator
    rz_grid = np.logspace(np.log10(RZ_MIN), np.log10(RZ_MAX), n_rz)
    s8_grid = np.zeros((n_rz, len(z_vals)))
    print(f"  Precomputing S₈ grid: {n_rz} × {len(z_vals)} = {n_rz*len(z_vals)} points...")
    for j, z in enumerate(z_vals):
        for i, rz in enumerate(rz_grid):
            s8_grid[i, j] = engine.predict_s8_z(z, rz, 0.0, use_nl=True)
    interp = RegularGridInterpolator(
        (np.log(rz_grid), np.array(z_vals)),
        s8_grid,
        method="linear",
        bounds_error=False,
        fill_value=None,
    )
    return rz_grid, interp


def s8_interp(interp, rz, z):
    rz_val = float(np.clip(rz, RZ_MIN, RZ_MAX))
    return float(interp([[np.log(rz_val), float(z)]])[0])


# ─── Cross-term model helpers ─────────────────────────────────────────────────
def compute_rz(k, z, A, gamma, beta0, dbeta):
    beta_eff = beta0 + dbeta * np.log(k)
    r0       = A * k ** (-gamma)
    return r0 * (1.0 + z) ** (-beta_eff)


# ─── P2 FIX: Constrained cost function ───────────────────────────────────────
def cross_term_cost_v2(params, training_surveys, interp):
    """
    χ² cost for cross-term model — P2 fix: physical constraints enforced.
    Bounds: A∈(1,200), γ∈(0.001,2), β₀∈(-5,10), δβ∈(-10,10)
    """
    A, gamma, beta0, dbeta = params
    # P2 fix: hard physical bounds via penalty
    if A <= A_MIN or A >= A_MAX:
        return 1e9
    if gamma <= GAMMA_MIN or gamma >= GAMMA_MAX:
        return 1e9
    if beta0 < BETA0_MIN or beta0 > BETA0_MAX:
        return 1e9
    if dbeta < DBETA_MIN or dbeta > DBETA_MAX:
        return 1e9

    chi2 = 0.0
    for sv in training_surveys.values():
        k_j, z_j = sv["k_eff"], sv["z_eff"]
        beta_eff_j = beta0 + dbeta * np.log(k_j)
        r0_j  = A * k_j ** (-gamma)
        rz_j  = r0_j * (1.0 + z_j) ** (-beta_eff_j)
        if rz_j <= 0:
            return 1e9
        s8_pred_j  = s8_interp(interp, rz_j, z_j)
        a_j        = 1.0 / (1.0 + z_j)
        s8_obs_z_j = sv["S8_obs"] * (a_j ** 0.55)
        s8_err_z_j = sv["S8_err"] * (a_j ** 0.55)
        chi2 += ((s8_pred_j - s8_obs_z_j) / s8_err_z_j) ** 2
    return chi2


def fit_cross_term_v2(training_surveys, interp, init=(10.0, 0.5, 2.0, 0.0)):
    """
    Optimize (A, γ, β₀, δβ) with physical constraints.
    P2 fix: bounded Nelder-Mead via penalty in cost function.
    Multiple restarts covering physical parameter space.
    """
    best_res  = None
    best_cost = np.inf

    inits = [
        (10.0, 0.5, 2.0,  0.0),
        (10.0, 0.5, 1.5,  0.5),
        (10.0, 0.5, 2.5, -0.5),
        (15.0, 0.4, 2.0,  0.0),
        (7.0,  0.5, 2.0,  1.0),
        (20.0, 0.3, 3.0,  0.5),
        (5.0,  0.8, 1.0, -0.5),
        (30.0, 0.2, 4.0, -1.0),
    ]
    for x0 in inits:
        res = minimize(
            cross_term_cost_v2,
            x0,
            args=(training_surveys, interp),
            method="Nelder-Mead",
            options={"xatol": 1e-5, "fatol": 1e-5, "maxiter": 10000},
        )
        if res.fun < best_cost:
            best_cost = res.fun
            best_res  = res

    return best_res.x, best_cost


# ─── P2 FIX: Sanity check for degenerate folds ───────────────────────────────
def check_fold_sanity(rz_pred_ho, beta_eff_ho, A_loo, gamma_loo):
    """
    P2 fix: Post-optimization sanity check per ng.md requirement.
    Returns (is_valid: bool, issues: list[str])
    """
    issues = []
    if rz_pred_ho < RZ_MIN or rz_pred_ho > RZ_MAX:
        issues.append(f"r_z={rz_pred_ho:.3f} outside [{RZ_MIN},{RZ_MAX}] Mpc/h")
    if beta_eff_ho <= 0:
        issues.append(f"beta_eff={beta_eff_ho:.4f} ≤ 0 (unphysical: (1+z) growth inverted)")
    if A_loo <= A_MIN:
        issues.append(f"A={A_loo:.4f} ≤ {A_MIN} (coherence radius collapsed)")
    return len(issues) == 0, issues


# ─── Section 1b v2: LOO-CV with physical constraints ─────────────────────────
def loo_cv_cross_term_v2(surveys, interp):
    """
    LOO-CV with P2-constrained optimization.
    Degenerate folds are flagged; MAE computed for valid folds + all folds separately.
    """
    names   = list(surveys.keys())
    results = {}

    for held_out in names:
        train = {n: surveys[n] for n in names if n != held_out}

        params_opt, train_chi2 = fit_cross_term_v2(train, interp)
        A, gamma, beta0, dbeta = params_opt

        sv     = surveys[held_out]
        k_ho   = sv["k_eff"]
        z_ho   = sv["z_eff"]
        b_eff  = beta0 + dbeta * np.log(k_ho)
        r0_ho  = A * k_ho ** (-gamma)
        rz_ho  = r0_ho * (1.0 + z_ho) ** (-b_eff)
        s8_pred = s8_interp(interp, rz_ho, z_ho)
        a_ho   = 1.0 / (1.0 + z_ho)
        s8_obs_z  = sv["S8_obs"] * (a_ho ** 0.55)
        s8_err_z  = sv["S8_err"] * (a_ho ** 0.55)
        tension   = (s8_pred - s8_obs_z) / s8_err_z

        is_valid, issues = check_fold_sanity(rz_ho, b_eff, A, gamma)

        results[held_out] = {
            "A_loo":        round(A, 4),
            "gamma_loo":    round(gamma, 4),
            "beta0_loo":    round(beta0, 4),
            "dbeta_loo":    round(dbeta, 4),
            "beta_eff_ho":  round(b_eff, 4),
            "rz_pred_ho":   round(rz_ho, 3),
            "s8_pred":      round(s8_pred, 4),
            "s8_obs_z":     round(s8_obs_z, 4),
            "s8_err_z":     round(s8_err_z, 4),
            "tension":      round(tension, 4),
            "train_chi2":   round(train_chi2, 4),
            "sanity_valid": is_valid,
            "sanity_issues": issues,
        }

    # Compute MAE for valid + all folds
    tensions_all   = [v["tension"] for v in results.values()]
    tensions_valid = [v["tension"] for k, v in results.items() if v["sanity_valid"]]
    valid_names    = [k for k, v in results.items() if v["sanity_valid"]]
    degen_names    = [k for k, v in results.items() if not v["sanity_valid"]]

    mae_all   = float(np.mean(np.abs(tensions_all)))  if tensions_all   else float('nan')
    mae_valid = float(np.mean(np.abs(tensions_valid))) if tensions_valid else float('nan')
    mae_excl_kids = float(np.mean([abs(v["tension"]) for k, v in results.items()
                                    if k != "KiDS-Legacy"])) if len(results) > 1 else float('nan')

    return {
        "per_fold":         results,
        "mae_all_folds":    round(mae_all, 4),
        "mae_valid_folds":  round(mae_valid, 4) if not math.isnan(mae_valid) else None,
        "mae_excl_kids":    round(mae_excl_kids, 4),
        "n_valid_folds":    len(valid_names),
        "n_degen_folds":    len(degen_names),
        "valid_fold_names": valid_names,
        "degen_fold_names": degen_names,
        "n_surveys":        len(names),
        "n_params":         4,
        "dof_ratio":        round(4.0 / len(names), 2),
        "freedom_note":     "4 params / 5 data points = 0.80 (over-fitting risk: HIGH per auditor directive)",
        "constraint_note":  "P2 fix: A∈(1,200), γ∈(0.001,2), β₀∈(-5,10), δβ∈(-10,10). Degenerate folds flagged by sanity check.",
    }


# ─── P1 FIX: KiDS z_eff variants ─────────────────────────────────────────────
def loo_cv_kids_zeff_variants(base_surveys, engine, z_all):
    """
    P1 fix: Re-run LOO-CV with 3 KiDS z_eff definitions.
    Builds extended grid covering all needed z values.
    """
    variants = {
        "z026_published":   0.26,
        "z526_mean_nz":     0.526,
        "z482_s8weighted":  0.482,
    }
    # Build extended grid covering all z values across variants
    z_extended = sorted(set(
        list(z_all) + [0.482, 0.526]
    ))
    print(f"  Building extended S₈ grid for z_eff variants: {z_extended}")
    _, interp_ext = precompute_s8_grid(engine, z_extended, n_rz=80)

    results = {}
    for variant_name, kids_zeff in variants.items():
        print(f"\n  Running LOO-CV with KiDS z_eff = {kids_zeff} ({variant_name})...")
        surveys_v = {}
        for name, sv in base_surveys.items():
            surveys_v[name] = dict(sv)
        surveys_v["KiDS-Legacy"]["z_eff"] = kids_zeff

        loo = loo_cv_cross_term_v2(surveys_v, interp_ext)

        kids_fold = loo["per_fold"]["KiDS-Legacy"]
        des_fold  = loo["per_fold"]["DES Y3"]
        results[variant_name] = {
            "kids_zeff_used":    kids_zeff,
            "mae_all_folds":     loo["mae_all_folds"],
            "mae_valid_folds":   loo["mae_valid_folds"],
            "mae_excl_kids":     loo["mae_excl_kids"],
            "n_valid_folds":     loo["n_valid_folds"],
            "n_degen_folds":     loo["n_degen_folds"],
            "degen_fold_names":  loo["degen_fold_names"],
            "kids_tension":      kids_fold["tension"],
            "kids_rz":           kids_fold["rz_pred_ho"],
            "kids_beta_eff":     kids_fold["beta_eff_ho"],
            "kids_sanity_valid": kids_fold["sanity_valid"],
            "kids_sanity_issues":kids_fold["sanity_issues"],
            "des_tension":       des_fold["tension"],
            "per_fold":          loo["per_fold"],
        }

    # Build comparison table
    comparison = []
    for vname, vdata in results.items():
        row = {
            "variant":          vname,
            "kids_zeff":        vdata["kids_zeff_used"],
            "KiDS_tension_σ":   round(vdata["kids_tension"], 4),
            "DES_tension_σ":    round(vdata["des_tension"], 4),
            "MAE_all_σ":        vdata["mae_all_folds"],
            "MAE_valid_σ":      vdata["mae_valid_folds"],
            "n_valid_folds":    vdata["n_valid_folds"],
        }
        comparison.append(row)

    return {
        "variants":   results,
        "comparison": comparison,
        "conclusion": _interpret_kids_variants(results),
    }


def _interpret_kids_variants(results):
    base   = results["z026_published"]
    mean   = results["z526_mean_nz"]
    s8w    = results["z482_s8weighted"]

    def delta_kids(v): return v["kids_tension"] - base["kids_tension"]

    lines = []
    lines.append(f"KiDS tension with z_eff=0.26 (published): {base['kids_tension']:+.4f}σ")
    lines.append(f"KiDS tension with z_eff=0.526 (mean n(z)): {mean['kids_tension']:+.4f}σ "
                 f"(Δ={delta_kids(mean):+.4f}σ vs published)")
    lines.append(f"KiDS tension with z_eff=0.482 (S8-weighted): {s8w['kids_tension']:+.4f}σ "
                 f"(Δ={delta_kids(s8w):+.4f}σ vs published)")
    if abs(mean["kids_tension"]) < abs(base["kids_tension"]):
        lines.append("RESULT: Updated z_eff REDUCES KiDS tension. Section 3 trigger was meaningful.")
    else:
        lines.append("RESULT: Updated z_eff does NOT reduce KiDS tension. "
                     "Published z_eff=0.26 (lensing-efficiency-weighted) is appropriate for this model.")
    return " | ".join(lines)


# ─── P3 FIX: AIC/BIC with corrected baseline_cost ────────────────────────────
def compute_aic_bic_v2(surveys, interp):
    """
    P3 fix: baseline_cost() now enforces γ>0 (and A>0).
    Other changes: consistent constraint handling across all three models.
    """
    n = 5

    # P3 FIX: Add gamma > 0 to baseline_cost
    def baseline_cost(params_2):
        A, gamma = params_2
        if A <= 0 or gamma <= 0:          # P3 fix: γ > 0 constraint added
            return 1e9
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

    # M0 — multiple restarts for robustness
    best_m0, best_m0_x = np.inf, None
    for x0 in [(10.0, 0.5), (20.0, 0.3), (5.0, 0.8), (50.0, 0.2), (30.0, 1.0)]:
        res = minimize(baseline_cost, x0, method="Nelder-Mead",
                       options={"xatol": 1e-6, "fatol": 1e-6, "maxiter": 10000})
        if res.fun < best_m0:
            best_m0 = float(res.fun)
            best_m0_x = res.x
    chi2_m0 = best_m0
    k0 = 2

    # M1: cross-term (4 params, physically constrained)
    params_m1, chi2_m1 = fit_cross_term_v2(surveys, interp)
    k1 = 4

    # M2: two-regime β (4 params, with constraints)
    def two_regime_cost(params):
        A, gamma, beta_low, beta_high = params
        if A <= 0 or gamma <= 0:
            return 1e9
        K_THRESH = 0.35
        chi2 = 0.0
        for sv in surveys.values():
            k, z = sv["k_eff"], sv["z_eff"]
            beta_eff = beta_low if k <= K_THRESH else beta_high
            rz = A * k ** (-gamma) * (1.0 + z) ** (-beta_eff)
            if rz <= 0:
                return 1e9
            s8_pred = s8_interp(interp, rz, z)
            a = 1.0 / (1.0 + z)
            s8_obs_z = sv["S8_obs"] * (a ** 0.55)
            s8_err_z = sv["S8_err"] * (a ** 0.55)
            chi2 += ((s8_pred - s8_obs_z) / s8_err_z) ** 2
        return chi2

    best_m2, best_m2_x = np.inf, None
    for x0 in [(10.0, 0.5, 2.0, 1.5), (15.0, 0.3, 3.0, 1.0), (8.0, 0.6, 1.5, 2.0)]:
        res = minimize(two_regime_cost, x0, method="Nelder-Mead",
                       options={"xatol": 1e-6, "fatol": 1e-6, "maxiter": 10000})
        if res.fun < best_m2:
            best_m2 = float(res.fun)
            best_m2_x = res.x
    chi2_m2 = best_m2
    k2 = 4

    def aic(k, chi2): return 2 * k + chi2
    def bic(k, chi2): return k * math.log(n) + chi2

    return {
        "n_data":      n,
        "note":        "AIC = 2k + χ²_min, BIC = k×ln(n) + χ²_min (Gaussian likelihood). P3 fix: M0 γ>0 enforced.",
        "p3_fix_note": "P3 fix applied: baseline_cost() now includes 'if A<=0 or gamma<=0: return 1e9'. v1 had gamma_fit=-0.9301 (unphysical).",
        "M0_baseline": {
            "model":     "R₀ = A × k^(-γ) × (1+z)^β_SSoT (2 params, β fixed, γ>0 enforced)",
            "k":         k0,
            "chi2":      round(chi2_m0, 4),
            "AIC":       round(aic(k0, chi2_m0), 4),
            "BIC":       round(bic(k0, chi2_m0), 4),
            "A_fit":     round(best_m0_x[0], 4),
            "gamma_fit": round(best_m0_x[1], 4),
            "gamma_positive_enforced": True,
        },
        "M1_cross_term": {
            "model": "R₀ = A × k^(-γ) × (1+z)^(β₀+δβ ln k) (4 params, physical constraints)",
            "k":     k1,
            "chi2":  round(chi2_m1, 4),
            "AIC":   round(aic(k1, chi2_m1), 4),
            "BIC":   round(bic(k1, chi2_m1), 4),
        },
        "M2_two_regime": {
            "model": "Two-regime β: β_low (k≤0.35) / β_high (k>0.35) (4 params)",
            "k":     k2,
            "chi2":  round(chi2_m2, 4),
            "AIC":   round(aic(k2, chi2_m2), 4),
            "BIC":   round(bic(k2, chi2_m2), 4),
        },
        "preferred_by_AIC": (
            "M0_baseline" if aic(k0, chi2_m0) <= min(aic(k1, chi2_m1), aic(k2, chi2_m2))
            else ("M1_cross_term" if aic(k1, chi2_m1) <= aic(k2, chi2_m2) else "M2_two_regime")
        ),
        "preferred_by_BIC": (
            "M0_baseline" if bic(k0, chi2_m0) <= min(bic(k1, chi2_m1), bic(k2, chi2_m2))
            else ("M1_cross_term" if bic(k1, chi2_m1) <= bic(k2, chi2_m2) else "M2_two_regime")
        ),
        "v1_comparison": {
            "v1_M0_gamma_fit": -0.9301,
            "v1_M0_chi2":       1.2747,
            "v1_M0_AIC":        5.2747,
            "v2_M0_gamma_fit":  round(best_m0_x[1], 4),
            "v2_M0_chi2":       round(chi2_m0, 4),
            "v2_M0_AIC":        round(aic(k0, chi2_m0), 4),
            "note": "v1 M0 had γ=-0.9301 (unphysical γ<0). v2 enforces γ>0.",
        },
    }


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 76)
    print("KSAU v25.0 Session 2 — Section 1 v2")
    print("Addresses: P1 (KiDS z_eff re-run), P2 (physical constraints), P3 (γ>0 baseline)")
    print("=" * 76)

    surveys = load_surveys()
    engine  = LOOCVFinalAudit(config_path=CONFIG_PATH)

    z_base = sorted(set(s["z_eff"] for s in surveys.values()))
    print(f"\nBase z_eff grid: {z_base}")

    # Build base interpolator (z_eff = 0.26 for KiDS)
    print("\nStep 1: Precomputing base S₈ grid...")
    _, interp_base = precompute_s8_grid(engine, z_base, n_rz=80)
    print(f"  Done. r_z range: [{RZ_MIN:.1f}, {RZ_MAX:.1f}] Mpc/h")

    # P2+P3 fix: LOO-CV with physical constraints on base data
    print("\nStep 2: LOO-CV with physical constraints (P2 fix)...")
    loo_v2 = loo_cv_cross_term_v2(surveys, interp_base)

    print(f"\n  LOO-CV MAE (all 5 folds)   = {loo_v2['mae_all_folds']:.4f}σ")
    print(f"  LOO-CV MAE (valid folds)   = {loo_v2['mae_valid_folds']}σ")
    print(f"  LOO-CV MAE (excl KiDS)     = {loo_v2['mae_excl_kids']:.4f}σ")
    print(f"  Valid folds: {loo_v2['valid_fold_names']}")
    print(f"  Degenerate folds: {loo_v2['degen_fold_names']}")

    print(f"\n  Per-fold results (v1 → v2 comparison):")
    print(f"  {'Survey':<14} {'v24.0':>8} {'v25.0_v1':>10} {'v25.0_v2':>10}  {'Valid':>6}  {'Issues'}")
    for name, fold in loo_v2["per_fold"].items():
        v24t = V24_TENSIONS[name]
        v1t  = V1_TENSIONS[name]
        v2t  = fold["tension"]
        ok   = "✓" if fold["sanity_valid"] else "✗"
        iss  = "; ".join(fold["sanity_issues"]) if fold["sanity_issues"] else "—"
        print(f"  {name:<14} {v24t:>+8.3f}σ {v1t:>+10.4f}σ {v2t:>+10.4f}σ {ok:>6}  {iss}")

    # P3 fix: AIC/BIC with corrected M0 baseline
    print("\nStep 3: AIC/BIC with P3 fix (γ>0 baseline constraint)...")
    aic_bic = compute_aic_bic_v2(surveys, interp_base)
    print(f"  M0 (γ>0 enforced): γ_fit={aic_bic['M0_baseline']['gamma_fit']:.4f}, "
          f"χ²={aic_bic['M0_baseline']['chi2']:.4f}, AIC={aic_bic['M0_baseline']['AIC']:.4f}")
    print(f"  M1 (cross-term):   χ²={aic_bic['M1_cross_term']['chi2']:.4f}, "
          f"AIC={aic_bic['M1_cross_term']['AIC']:.4f}")
    print(f"  M2 (two-regime):   χ²={aic_bic['M2_two_regime']['chi2']:.4f}, "
          f"AIC={aic_bic['M2_two_regime']['AIC']:.4f}")
    print(f"  Preferred (AIC): {aic_bic['preferred_by_AIC']}")
    print(f"  Preferred (BIC): {aic_bic['preferred_by_BIC']}")
    print(f"  P3 fix: v1 γ_fit={aic_bic['v1_comparison']['v1_M0_gamma_fit']} → "
          f"v2 γ_fit={aic_bic['v1_comparison']['v2_M0_gamma_fit']}")

    # P1 fix: KiDS z_eff variants
    print("\nStep 4: KiDS z_eff variants LOO-CV (P1 fix)...")
    kids_variants = loo_cv_kids_zeff_variants(surveys, engine, z_base)

    print(f"\n  KiDS z_eff comparison table:")
    print(f"  {'Variant':<22} {'z_eff':>6} {'KiDS_t':>8} {'DES_t':>8} {'MAE_all':>9} {'MAE_valid':>10} {'Valid/5':>8}")
    for row in kids_variants["comparison"]:
        print(f"  {row['variant']:<22} {row['kids_zeff']:>6.3f} "
              f"{row['KiDS_tension_σ']:>+8.4f}σ {row['DES_tension_σ']:>+8.4f}σ "
              f"{row['MAE_all_σ']:>9.4f}σ "
              f"{str(row['MAE_valid_σ']):>10}σ "
              f"{row['n_valid_folds']:>4}/5")
    print(f"\n  Conclusion: {kids_variants['conclusion']}")

    # Compile results
    results = {
        "date":    "2026-02-18",
        "session": "v25.0 Session 2",
        "section": "Section 1 v2",
        "ng_md_addressed": ["P1 (KiDS z_eff rerun)", "P2 (physical constraints)", "P3 (gamma>0 baseline)"],
        "ssot": {
            "kappa":       KAPPA,
            "alpha":       ALPHA,
            "beta_ssot":   BETA_SSoT,
            "r_base_ssot": R_BASE_SSoT,
        },
        "physical_constraints_applied": {
            "A":     f"({A_MIN}, {A_MAX})",
            "gamma": f"({GAMMA_MIN}, {GAMMA_MAX})",
            "beta0": f"({BETA0_MIN}, {BETA0_MAX})",
            "dbeta": f"({DBETA_MIN}, {DBETA_MAX})",
            "post_opt_sanity": f"r_z∈[{RZ_MIN},{RZ_MAX}] Mpc/h AND beta_eff>0",
        },
        "v24_baseline": {"mae_sigma": 1.030},
        "v25_v1_loo_mae": 1.6253,
        "section_1b_loo_cv_v2":      loo_v2,
        "section_1_aic_bic_v2":      aic_bic,
        "section_p1_kids_zeff_variants": kids_variants,
    }

    out_path = BASE / "v25.0" / "data" / "section_1_results_v2.json"
    with open(str(out_path), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved → {out_path}")
    return results


if __name__ == "__main__":
    main()
