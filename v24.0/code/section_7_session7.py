#!/usr/bin/env python3
"""
KSAU v24.0 Section 7 — Session 7: ng.md Session 6 REJECT Response
==================================================================
Addressing ALL requirements from ng.md (Session 6 verdict):

  CRITICAL FLAW #1 (P1): R-6 permutation test was NOT testing SSoT prediction
    - Option A: Re-run permutation test with SSoT-fixed quintuple {7,6,5,3,1}
    - Report p-value for constrained (SSoT-only) test
    - Disclose that SSoT quintuple gives CV=19.49% (not 6.66%)

  CRITICAL FLAW #2 (P1): Comparison table uses inconsistent baselines
    - Report deviation from actual best-fit quintuple {8,5,4,3,2} (4.9%)
    - Report 13.7% deviation of best-fit R_base from SSoT formula 3/(2κ)

  MODERATE FLAW #3 (P2): Bootstrap "ROBUST" at p=0.316 is unjustified
    - Remove hardcoded p_mc >= 0.20 threshold
    - Report Bootstrap p=0.316 as "MODERATE ROBUSTNESS" with honest interpretation
    - Rely on B+P combined test (76%) as PRIMARY robustness metric

  MODERATE FLAW #4 (P2): β_KiDS-fold causal interpretation inverted
    - Correct: "Including KiDS pushes β from ~1.0 to ~3.1"
    - NOT: "KiDS requires β ≈ 1.0"

  P3 (NEW): R-3 — k_eff-dependent correction term f(k_eff) in R₀
    - Fit: R₀(k_eff) = A × k_eff^(-γ) parametrization using LOO-CV R₀
    - Test CV reduction with this k_eff-dependent model

Author: KSAU v24.0 Simulation Kernel — Session 7
Date:   2026-02-18
References: v24.0/ng.md (Session 6 REJECT Verdict)
"""

import sys, os, json, itertools, math
import numpy as np
from pathlib import Path
from scipy.optimize import minimize, curve_fit

BASE = Path("E:/Obsidian/KSAU_Project")
sys.path.insert(0, str(BASE / "v23.0" / "code"))
from loo_cv_engine_v23_final_audit import LOOCVFinalAudit

CONFIG_PATH = str(BASE / "v23.0" / "data" / "cosmological_constants.json")
WL5_CONFIG  = str(BASE / "v24.0" / "data" / "wl5_survey_config.json")

# SSoT: Leech shell magnitudes (r² = 2,4,...,16)
LEECH_SHELLS = {
    1: math.sqrt(2),    # r² = 2  → mag = √2 ≈ 1.4142
    2: 2.0,             # r² = 4  → mag = 2.0
    3: math.sqrt(6),    # r² = 6  → mag = √6 ≈ 2.4495
    4: 2 * math.sqrt(2),# r² = 8  → mag = 2√2 ≈ 2.8284
    5: math.sqrt(10),   # r² = 10 → mag = √10 ≈ 3.1623
    6: 2 * math.sqrt(3),# r² = 12 → mag = 2√3 ≈ 3.4641
    7: math.sqrt(14),   # r² = 14 → mag = √14 ≈ 3.7417
    8: 4.0,             # r² = 16 → mag = 4.0
}
QUINTUPLES = [tuple(reversed(c)) for c in itertools.combinations(range(1, 9), 5)]

# SSoT-predicted quintuple (shells for DES→CFHTLenS→DLS→HSC→KiDS, by k_eff asc)
SSOT_QUINTUPLE = (7, 6, 5, 3, 1)  # ordered by k_eff ascending (DES,CFHTLenS,DLS,HSC,KiDS)

# Best-fit quintuple found in Session 5/6 (minimizes CV for physical R₀ ordering)
BESTFIT_QUINTUPLE = (8, 5, 4, 3, 2)  # {DES→8, CFHTLenS→5, DLS→4, HSC→3, KiDS→2}


# ══════════════════════════════════════════════════════════════════════════════
#  UTILITY: CV for a fixed shell quintuple assignment
# ══════════════════════════════════════════════════════════════════════════════

def cv_for_fixed_quintuple(r0_arr, quintuple):
    """Compute CV of R_base = R₀_i / shell_mag_i for a FIXED quintuple."""
    r_bases = np.array([r0_arr[i] / LEECH_SHELLS[quintuple[i]] for i in range(5)])
    return float(r_bases.std() / r_bases.mean()), r_bases


def best_cv_for_assignment(r0_arr):
    """Find minimum CV over all C(8,5)=56 shell quintuples for given R₀ array."""
    best_cv = float("inf")
    best_qt = None
    for qt in QUINTUPLES:
        cv, _ = cv_for_fixed_quintuple(r0_arr, qt)
        if cv < best_cv:
            best_cv = cv
            best_qt = qt
    return best_cv, best_qt


# ══════════════════════════════════════════════════════════════════════════════
#  UTILITY: Load 5 WL surveys
# ══════════════════════════════════════════════════════════════════════════════

def load_wl5_surveys():
    with open(WL5_CONFIG, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    surveys = cfg["surveys"]
    ordered = dict(sorted(surveys.items(), key=lambda x: x[1]["k_eff"]))
    ssot_leech = cfg["expected_leech_assignment"]
    return ordered, ssot_leech


# ══════════════════════════════════════════════════════════════════════════════
#  P1a: SSoT-CONSTRAINED PERMUTATION TEST
#  Critical Flaw #1 fix: test ONLY the SSoT quintuple {7,6,5,3,1}
# ══════════════════════════════════════════════════════════════════════════════

def ssot_constrained_permutation_test(loo_r0, surveys_ordered):
    """
    SSoT-constrained permutation test (Option A from ng.md P1).

    PROBLEM (ng.md Flaw #1): Session 5/6 permutation test searched all 56
    quintuples and found p=0.0167 for the best-fit quintuple {8,5,4,3,2}.
    This does NOT test the SSoT prediction {7,6,5,3,1}.

    FIX: Lock the quintuple to SSoT-predicted {7,6,5,3,1} for ALL permutations.
    Test: "Does the physical k_eff-sorted R₀ ordering give lower CV than 119 other
    orderings, when ONLY SSoT quintuple shells are used for CV computation?"

    The physical ordering (by k_eff ascending): DES→CFHTLenS→DLS→HSC→KiDS
    (This corresponds to descending R₀, as larger k_eff → smaller R₀.)
    """
    r0_vals = np.array([loo_r0[n] for n in surveys_ordered])

    # CV for physical ordering under SSoT quintuple
    physical_cv, physical_r_bases = cv_for_fixed_quintuple(r0_vals, SSOT_QUINTUPLE)
    physical_r_base_mean = float(physical_r_bases.mean())

    # Enumerate ALL 120 permutations of R₀ values (keep quintuple fixed)
    all_cvs = []
    n_beats = 0
    for perm in itertools.permutations(r0_vals):
        perm_cv, _ = cv_for_fixed_quintuple(np.array(perm), SSOT_QUINTUPLE)
        all_cvs.append(perm_cv)
        if perm_cv <= physical_cv * 1.0001:
            n_beats += 1

    p_ssot = n_beats / 120.0
    rank = sorted(all_cvs).index(physical_cv) + 1  # rank from best (lowest CV)

    # Also: what does the previous best-fit quintuple give for the physical ordering?
    bestfit_cv, bestfit_r_bases = cv_for_fixed_quintuple(r0_vals, BESTFIT_QUINTUPLE)
    bestfit_r_base_mean = float(bestfit_r_bases.mean())

    return {
        "ssot_quintuple": list(SSOT_QUINTUPLE),
        "ssot_quintuple_shells": {surveys_ordered[i]: SSOT_QUINTUPLE[i] for i in range(5)},
        "physical_cv_ssot_pct": float(physical_cv * 100.0),
        "physical_r_base_ssot": physical_r_base_mean,
        "r_base_ssot_formula": 3.0 / (2.0 * math.pi / 24.0),
        "n_beats": n_beats,
        "n_permutations": 120,
        "p_value_ssot_constrained": float(p_ssot),
        "rank_of_physical": rank,
        "pass_p_lt_005": p_ssot < 0.05,
        "ssot_cv_note": (
            f"CV with SSoT quintuple {{{','.join(map(str,SSOT_QUINTUPLE))}}} "
            f"for physical ordering = {physical_cv*100:.2f}% "
            f"(vs 6.66% from best-fit quintuple). "
            f"Physical ordering is rank {rank}/120 under SSoT-fixed quintuple."
        ),
        "session6_comparison": {
            "session6_quintuple": list(BESTFIT_QUINTUPLE),
            "session6_cv_pct": float(bestfit_cv * 100.0),
            "session6_r_base": float(bestfit_r_base_mean),
            "session6_r_base_ssot": 3.0 / (2.0 * math.pi / 24.0),
            "session6_r_base_deviation_from_ssot_pct": float(
                (bestfit_r_base_mean - 3.0 / (2.0 * math.pi / 24.0))
                / (3.0 / (2.0 * math.pi / 24.0)) * 100.0
            ),
        },
    }


# ══════════════════════════════════════════════════════════════════════════════
#  P1b: BEST-FIT QUINTUPLE BASELINE DISCLOSURE
#  Critical Flaw #2 fix: report deviation from ACTUAL computation quintuple
# ══════════════════════════════════════════════════════════════════════════════

def bestfit_quintuple_disclosure(loo_r0, surveys_ordered, r_base_ssot):
    """
    P1b: Report deviation of LOO-CV R₀ from the ACTUAL best-fit quintuple used
    in the permutation test, and disclose the 13.7% SSoT R_base deviation.

    ng.md Flaw #2: Session 6 comparison table reported deviations from SSoT
    quintuple {7,6,5,3,1} with R_base=11.459. But the computation actually
    used {8,5,4,3,2} with R_base≈9.896. Presenting 17.1% as "Leech deviation"
    is misleading; the actual computation deviation is 4.9%.
    """
    r0_vals = np.array([loo_r0[n] for n in surveys_ordered])

    # Best-fit quintuple {8,5,4,3,2} analysis
    bestfit_cv, bestfit_r_bases = cv_for_fixed_quintuple(r0_vals, BESTFIT_QUINTUPLE)
    r_base_bestfit = float(bestfit_r_bases.mean())

    # Per-survey deviation from best-fit quintuple
    rows_bestfit = []
    for i, name in enumerate(surveys_ordered):
        shell = BESTFIT_QUINTUPLE[i]
        shell_mag = LEECH_SHELLS[shell]
        r0_predicted = r_base_bestfit * shell_mag
        deviation = (r0_vals[i] - r0_predicted) / r0_predicted * 100.0
        rows_bestfit.append({
            "survey": name,
            "bestfit_shell": shell,
            "shell_mag": round(shell_mag, 4),
            "r0_bestfit_predicted": round(r0_predicted, 3),
            "loo_cv_r0": round(float(r0_vals[i]), 3),
            "deviation_from_bestfit_pct": round(float(deviation), 2),
        })
    mean_dev_bestfit = float(np.mean([abs(r["deviation_from_bestfit_pct"]) for r in rows_bestfit]))

    # Deviation of best-fit R_base from SSoT formula
    r_base_deviation_pct = (r_base_bestfit - r_base_ssot) / r_base_ssot * 100.0

    return {
        "_flaw_addressed": "Critical Flaw #2 from ng.md Session 6",
        "bestfit_quintuple": list(BESTFIT_QUINTUPLE),
        "bestfit_quintuple_shells": {surveys_ordered[i]: BESTFIT_QUINTUPLE[i] for i in range(5)},
        "r_base_bestfit": float(r_base_bestfit),
        "r_base_ssot": float(r_base_ssot),
        "r_base_deviation_from_ssot_pct": float(r_base_deviation_pct),
        "bestfit_cv_pct": float(bestfit_cv * 100.0),
        "per_survey_deviation_from_bestfit": rows_bestfit,
        "mean_abs_deviation_from_bestfit_pct": float(mean_dev_bestfit),
        "session6_reported_deviation_pct": 17.1,
        "disclosure_statement": (
            f"Session 6 reported mean |deviation| = 17.1% using SSoT quintuple "
            f"{{7,6,5,3,1}} with R_base = {r_base_ssot:.3f} Mpc/h. "
            f"The actual computation used quintuple {{8,5,4,3,2}} with "
            f"R_base = {r_base_bestfit:.3f} Mpc/h. "
            f"Deviation from ACTUAL computation: {mean_dev_bestfit:.1f}% (not 17.1%). "
            f"The best-fit R_base = {r_base_bestfit:.3f} Mpc/h deviates from "
            f"SSoT formula 3/(2κ) = {r_base_ssot:.3f} Mpc/h by {abs(r_base_deviation_pct):.1f}%. "
            f"This 13.7% deviation from the SSoT R_base is a measure of the Leech "
            f"lattice hypothesis failure; it was NOT disclosed in Session 6."
        ),
    }


# ══════════════════════════════════════════════════════════════════════════════
#  P2a: CORRECTED β_KiDS-FOLD CAUSAL INTERPRETATION
# ══════════════════════════════════════════════════════════════════════════════

def corrected_beta_interpretation(s6_beta_dispersion):
    """
    P2a: Correct the causal interpretation of β_KiDS-fold.

    WRONG (Session 6): "β_KiDS-fold = 1.00 → KiDS requires β ≈ 1.0"

    CORRECT:
    - β_KiDS-fold = 1.00 is the β estimated when KiDS is EXCLUDED from training
    - i.e., the 4 surveys {DES, CFHTLenS, DLS, HSC} alone prefer β ≈ 1.0
    - Including KiDS in training DRIVES β UP to ~3.1
    - KiDS (z_eff=0.26, k_eff=0.70) is the primary driver of β toward high values
    """
    kids_fold_beta = s6_beta_dispersion["kids_fold_beta"]
    mean_others = s6_beta_dispersion["mean_other_folds_beta"]
    delta_beta = s6_beta_dispersion["beta_delta_kids_vs_others"]

    return {
        "_flaw_addressed": "Moderate Flaw #4 from ng.md Session 6",
        "session6_wrong_statement": (
            f"β_KiDS-fold = {kids_fold_beta:.3f} vs β_others mean = {mean_others:.3f} "
            f"→ KiDS requires β ≈ 1.0 [INCORRECT CAUSAL INFERENCE]"
        ),
        "corrected_statement": (
            f"β_KiDS-fold = {kids_fold_beta:.3f} is the β estimated when KiDS is "
            f"EXCLUDED from training (i.e., DES + CFHTLenS + DLS + HSC alone). "
            f"The 4-survey dataset without KiDS prefers β ≈ {kids_fold_beta:.2f}. "
            f"Including KiDS in training drives β upward to ~{mean_others:.1f}. "
            f"KiDS (low z_eff=0.26, high k_eff=0.70) is the primary driver pushing β "
            f"from ~1.0 toward ~{mean_others:.1f}. "
            f"The correct conclusion: KiDS exerts dominant leverage on β estimation; "
            f"β is non-universal (Δβ = {delta_beta:.2f} when KiDS is included vs excluded)."
        ),
        "causal_direction": {
            "without_KiDS": f"β ≈ {kids_fold_beta:.2f} (4 surveys: DES, CFHTLenS, DLS, HSC)",
            "with_KiDS": f"β ≈ {mean_others:.2f} (all 5 surveys including KiDS)",
            "KiDS_effect": f"KiDS inclusion increases β by Δβ = +{abs(delta_beta):.2f}",
        },
        "what_is_correct": (
            "β non-universality diagnosis (Δβ = -2.12) stands. "
            "Only the causal attribution is corrected: KiDS DRIVES β high (not low)."
        ),
    }


# ══════════════════════════════════════════════════════════════════════════════
#  P2b: BOOTSTRAP ROBUSTNESS — HONEST REPORTING (remove p_mc >= 0.20 threshold)
# ══════════════════════════════════════════════════════════════════════════════

def honest_bootstrap_robustness_report(s6_bootstrap_mc, s6_bootstrap_perm):
    """
    P2b: Remove hardcoded 'ROBUST' threshold at p_mc >= 0.20.
    Provide honest interpretation of Bootstrap MC p=0.316.
    Report B+P combined test (76%) as PRIMARY metric.

    ng.md Flaw #3:
    - p_mc >= 0.20 → "ROBUST" has no statistical basis
    - p = 0.316 means 68.35% of noisy trials DEGRADE CV below actual
    - This is "MODERATE ROBUSTNESS" at best, not "ROBUST"
    - The B+P combined test (76% trials maintain p<0.05) is the rigorous metric
    """
    p_mc = s6_bootstrap_mc.get("p_value_bootstrap_mc_corrected", 0.3165)
    frac_degraded = 1.0 - p_mc
    frac_bp_p05 = s6_bootstrap_perm.get("fraction_trials_p_lt_005", 0.76)

    return {
        "_flaw_addressed": "Moderate Flaw #3 from ng.md Session 6",
        "bootstrap_mc_p": float(p_mc),
        "bootstrap_mc_interpretation": (
            f"Bootstrap MC p = {p_mc:.4f}. "
            f"In {frac_degraded:.1%} of Bootstrap trials, adding ±10% noise "
            f"DEGRADES CV below the actual CV. "
            f"Correct label: MODERATE ROBUSTNESS — NOT 'ROBUST'. "
            f"Threshold p_mc >= 0.20 → 'ROBUST' has no statistical basis and is REMOVED."
        ),
        "removed_threshold": "p_mc >= 0.20 → 'ROBUST' (hardcoded, no basis)",
        "revised_bootstrap_label": (
            "MODERATE ROBUSTNESS (p_MC=0.316; Bootstrap MC alone insufficient)"
        ),
        "primary_robustness_metric": {
            "metric": "Combined Bootstrap + Permutation test",
            "result": f"{frac_bp_p05:.0%} of Bootstrap trials maintain p < 0.05",
            "verdict": (
                "ROBUST (B+P primary metric): "
                f"Under ±10% noise, {frac_bp_p05:.0%} of trials maintain p < 0.05. "
                "This is the principled robustness measure for R-6."
            ),
        },
        "correct_r6_robustness_statement": (
            f"R-6 robustness relies on the B+P combined test: {frac_bp_p05:.0%} of Bootstrap "
            f"trials maintain p < 0.05 (median per-trial p = 0.025). "
            f"Bootstrap MC alone (p = {p_mc:.3f}) is a secondary metric indicating "
            f"MODERATE robustness of the CV magnitude to noise. "
            f"The permutation test significance (ordering) is the primary claim."
        ),
    }


# ══════════════════════════════════════════════════════════════════════════════
#  P3: R-3 — k_eff-DEPENDENT CORRECTION TERM f(k_eff)
# ══════════════════════════════════════════════════════════════════════════════

def r3_keff_correction(loo_r0, surveys, beta_fixed):
    """
    P3: Implement k_eff-dependent correction: R₀(k_eff, z) = A × k_eff^(-γ) × (1+z)^β

    MOTIVATION: β non-universality (R-S6-3) suggests the scaling
    R₀ ∝ k_eff^(-1) × (1+z)^β has residual k_eff dependence.

    MODEL: R₀ = A × k_eff^(-γ) × (1+z)^β

    Fit A and γ using 5 LOO-CV R₀ values (k_eff-ordered survey data).
    Then compute the implied k_eff-invariant CV.
    """
    names  = list(surveys.keys())
    r0_arr = np.array([loo_r0[n] for n in names])
    k_arr  = np.array([surveys[n]["k_eff"] for n in names])
    z_arr  = np.array([surveys[n]["z_eff"] for n in names])

    # Remove z-evolution to get r_z at each survey's z_eff: r_z = R₀ × (1+z)^(-β)
    r0_z_corrected = r0_arr / (1 + z_arr) ** beta_fixed

    # Fit R0_z_corrected = A * k_eff^(-gamma)
    def model(k, A, gamma):
        return A * k ** (-gamma)

    try:
        popt, pcov = curve_fit(
            model,
            k_arr,
            r0_z_corrected,
            p0=[30.0, 0.5],
            bounds=([0.1, 0.0], [500.0, 3.0]),
            maxfev=5000,
        )
        A_fit, gamma_fit = float(popt[0]), float(popt[1])
        fit_success = True
    except Exception as e:
        A_fit, gamma_fit, fit_success = 30.0, 0.5, False

    # Compute predicted R₀ for each survey (training: all 5, no LOO for fitting)
    r0_pred_full = np.array([A_fit * k ** (-gamma_fit) / (1 + z) ** (-beta_fixed)
                              for k, z in zip(k_arr, z_arr)])
    r0_pred_z_corrected = A_fit * k_arr ** (-gamma_fit)

    # Residuals from fit: R0_z_corrected - R0_pred_z_corrected
    residuals_pct = (r0_z_corrected - r0_pred_z_corrected) / r0_pred_z_corrected * 100.0

    # LOO-CV for R-3: for each held-out survey, fit A, gamma on 4 training surveys
    loo_tensions = {}
    loo_r0_predicted = {}
    for excluded in names:
        training_names = [n for n in names if n != excluded]
        k_train = np.array([surveys[n]["k_eff"] for n in training_names])
        z_train = np.array([surveys[n]["z_eff"] for n in training_names])
        r0_train = np.array([loo_r0[n] for n in training_names])
        r0_z_corr_train = r0_train / (1 + z_train) ** beta_fixed

        try:
            popt_loo, _ = curve_fit(
                model,
                k_train,
                r0_z_corr_train,
                p0=[30.0, 0.5],
                bounds=([0.1, 0.0], [500.0, 3.0]),
                maxfev=5000,
            )
            A_loo, gamma_loo = float(popt_loo[0]), float(popt_loo[1])
        except Exception:
            A_loo, gamma_loo = A_fit, gamma_fit

        obs = surveys[excluded]
        k_ho = obs["k_eff"]
        z_ho = obs["z_eff"]
        r0_predicted = A_loo * k_ho ** (-gamma_loo) / (1 + z_ho) ** (-beta_fixed)
        loo_r0_predicted[excluded] = float(r0_predicted)

        # Compute tension with r0_predicted
        from loo_cv_engine_v23_final_audit import LOOCVFinalAudit
        eng = LOOCVFinalAudit(config_path=CONFIG_PATH)
        a = 1.0 / (1.0 + z_ho)
        s8_pred = eng.predict_s8_z(z_ho, r0_predicted, beta_fixed, True)
        s8_obs_z = obs["S8_obs"] * (a ** 0.55)
        s8_err_z = obs["S8_err"] * (a ** 0.55)
        tension = (s8_pred - s8_obs_z) / s8_err_z
        loo_tensions[excluded] = {
            "k_eff": k_ho,
            "z_eff": z_ho,
            "r0_predicted": round(float(r0_predicted), 3),
            "r0_loo_s5": round(float(loo_r0[excluded]), 3),
            "s8_pred": round(float(s8_pred), 4),
            "s8_obs_z": round(float(s8_obs_z), 4),
            "tension_sigma": round(float(tension), 4),
        }

    mae = float(np.mean([abs(v["tension_sigma"]) for v in loo_tensions.values()]))
    tensions_list = [v["tension_sigma"] for v in loo_tensions.values()]
    n_lt15 = sum(1 for t in tensions_list if abs(t) < 1.5)
    n_lt1  = sum(1 for t in tensions_list if abs(t) < 1.0)

    # k_eff invariant CV from the fit
    inv_vals = A_fit * k_arr ** (-gamma_fit)  # these should be constant if model is good
    inv_cv = float(np.std(inv_vals) / np.mean(inv_vals) * 100.0) if np.mean(inv_vals) > 0 else 99.9

    # Original R_0 * k_eff^gamma / (1+z)^beta invariant CV
    invariant_with_fit = r0_z_corrected * k_arr ** gamma_fit
    inv_fit_cv = float(np.std(invariant_with_fit) / np.mean(invariant_with_fit) * 100.0)

    per_survey = []
    for i, name in enumerate(names):
        per_survey.append({
            "survey": name,
            "k_eff": k_arr[i],
            "z_eff": z_arr[i],
            "r0_loo_s5": round(float(r0_arr[i]), 3),
            "r0_z_corrected": round(float(r0_z_corrected[i]), 3),
            "r0_z_corr_predicted": round(float(r0_pred_z_corrected[i]), 3),
            "residual_pct": round(float(residuals_pct[i]), 2),
        })

    return {
        "model": "R₀(k_eff, z) = A × k_eff^(-γ) × (1+z)^β",
        "A_fit": float(A_fit),
        "gamma_fit": float(gamma_fit),
        "beta_fixed": float(beta_fixed),
        "fit_success": fit_success,
        "per_survey_fit": per_survey,
        "loo_cv_r3": loo_tensions,
        "mae_sigma_r3": round(mae, 4),
        "n_lt15_sigma": n_lt15,
        "n_lt1_sigma": n_lt1,
        "r3_pass": n_lt15 == 5,
        "inv_fit_cv_pct": round(inv_fit_cv, 2),
        "interpretation": (
            f"R₀ = {A_fit:.2f} × k_eff^(-{gamma_fit:.3f}) × (1+z)^{beta_fixed:.4f}. "
            f"k_eff-dependent fit: γ = {gamma_fit:.3f} (power-law slope). "
            f"LOO-CV MAE = {mae:.3f}σ. "
            f"Surveys with |tension| < 1.5σ: {n_lt15}/5. "
            + ("R-3 CV target check: " + str(round(inv_fit_cv, 1)) + "% "
               + ("< 10% ✓" if inv_fit_cv < 10.0 else "> 10% ✗"))
        ),
    }


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 76)
    print("KSAU v24.0 Section 7 — Session 7: ng.md Session 6 REJECT Response")
    print("Addressing: P1 (Critical Flaws #1,#2), P2 (Moderate Flaws #3,#4), P3 (R-3)")
    print("=" * 76)

    engine      = LOOCVFinalAudit(config_path=CONFIG_PATH)
    kappa       = engine.kappa
    alpha       = engine.alpha
    beta_fixed  = engine.beta_geo
    r_base_ssot = 3.0 / (2.0 * kappa)

    print(f"\nSSoT: κ = {kappa:.8f}, α = {alpha:.8f}, β = {beta_fixed:.6f}")
    print(f"      R_base_SSoT = 3/(2κ) = {r_base_ssot:.4f} Mpc/h")

    surveys, ssot_leech = load_wl5_surveys()
    surveys_ordered = list(surveys.keys())

    # Load Session 5 LOO-CV results (canonical R₀ values used in Sessions 5 & 6)
    s5_path = str(BASE / "v24.0" / "data" / "section_5_session5_results.json")
    with open(s5_path, "r", encoding="utf-8") as f:
        s5 = json.load(f)
    loo_r0 = {k: v["r0_opt"] for k, v in s5["r1_loo_cv_5wl"]["iterations"].items()}

    # Load Session 6 results for Bootstrap MC data
    s6_path = str(BASE / "v24.0" / "data" / "section_6_session6_results.json")
    with open(s6_path, "r", encoding="utf-8") as f:
        s6 = json.load(f)

    results = {
        "date": "2026-02-18",
        "session": 7,
        "kappa": float(kappa),
        "alpha": float(alpha),
        "beta_fixed": float(beta_fixed),
        "r_base_ssot": float(r_base_ssot),
    }

    # ══════════════════════════════════════════════════════════════════════
    # P1a: SSoT-CONSTRAINED PERMUTATION TEST
    # ══════════════════════════════════════════════════════════════════════
    print("\n" + "═" * 76)
    print("P1a: SSoT-CONSTRAINED PERMUTATION TEST (Critical Flaw #1)")
    print(f"  SSoT quintuple: {SSOT_QUINTUPLE}")
    print(f"  Session 6 used best-fit quintuple: {BESTFIT_QUINTUPLE}")
    print("═" * 76)

    r0_vals = np.array([loo_r0[n] for n in surveys_ordered])

    # Verify Session 6 claim: best-fit quintuple CV = 6.66%
    bestfit_cv_val, bestfit_qt = best_cv_for_assignment(r0_vals)
    print(f"\n  Best-fit quintuple: {bestfit_qt} → CV = {bestfit_cv_val*100:.2f}%")
    print(f"  SSoT quintuple {SSOT_QUINTUPLE} → CV = "
          f"{cv_for_fixed_quintuple(r0_vals, SSOT_QUINTUPLE)[0]*100:.2f}%")

    ssot_perm = ssot_constrained_permutation_test(loo_r0, surveys_ordered)
    p_ssot = ssot_perm["p_value_ssot_constrained"]
    physical_cv_ssot = ssot_perm["physical_cv_ssot_pct"]

    print(f"\n  SSoT-constrained permutation test:")
    print(f"    Physical R₀ ordering CV (SSoT quintuple): {physical_cv_ssot:.2f}%")
    print(f"    p-value (SSoT-fixed): {p_ssot:.4f}")
    print(f"    Rank of physical ordering: {ssot_perm['rank_of_physical']}/120")
    print(f"    Pass (p < 0.05): {ssot_perm['pass_p_lt_005']}")
    results["p1a_ssot_constrained_permutation"] = ssot_perm

    # ══════════════════════════════════════════════════════════════════════
    # P1b: BEST-FIT QUINTUPLE BASELINE DISCLOSURE
    # ══════════════════════════════════════════════════════════════════════
    print("\n" + "═" * 76)
    print("P1b: BEST-FIT QUINTUPLE BASELINE DISCLOSURE (Critical Flaw #2)")
    print("═" * 76)

    disclosure = bestfit_quintuple_disclosure(loo_r0, surveys_ordered, r_base_ssot)
    print(f"\n  Best-fit quintuple {BESTFIT_QUINTUPLE}:")
    print(f"    R_base (best-fit) = {disclosure['r_base_bestfit']:.4f} Mpc/h")
    print(f"    R_base (SSoT)     = {disclosure['r_base_ssot']:.4f} Mpc/h")
    print(f"    R_base deviation from SSoT = {abs(disclosure['r_base_deviation_from_ssot_pct']):.1f}%")
    print(f"\n  Per-survey deviation from ACTUAL best-fit quintuple:")
    print(f"  {'Survey':<18}  {'Shell':>5}  {'Predicted R₀':>12}  {'LOO-CV R₀':>10}  {'Dev%':>8}")
    print(f"  {'-'*18}  {'-'*5}  {'-'*12}  {'-'*10}  {'-'*8}")
    for r in disclosure["per_survey_deviation_from_bestfit"]:
        print(f"  {r['survey']:<18}  {r['bestfit_shell']:>5}  "
              f"{r['r0_bestfit_predicted']:>12.3f}  {r['loo_cv_r0']:>10.3f}  "
              f"{r['deviation_from_bestfit_pct']:>8.2f}%")
    print(f"\n  Mean |deviation| from best-fit quintuple: {disclosure['mean_abs_deviation_from_bestfit_pct']:.1f}%")
    print(f"  (Session 6 reported 17.1% using SSoT quintuple — inconsistent baseline)")
    results["p1b_bestfit_quintuple_disclosure"] = disclosure

    # ══════════════════════════════════════════════════════════════════════
    # P2a: CORRECTED β CAUSAL INTERPRETATION
    # ══════════════════════════════════════════════════════════════════════
    print("\n" + "═" * 76)
    print("P2a: CORRECTED β_KiDS-FOLD CAUSAL INTERPRETATION (Moderate Flaw #4)")
    print("═" * 76)

    beta_disp = s6["rs6_3_beta_dispersion"]
    corrected_beta = corrected_beta_interpretation(beta_disp)
    print(f"\n  WRONG (Session 6): {corrected_beta['session6_wrong_statement']}")
    print(f"\n  CORRECTED: {corrected_beta['corrected_statement']}")
    results["p2a_corrected_beta_interpretation"] = corrected_beta

    # ══════════════════════════════════════════════════════════════════════
    # P2b: HONEST BOOTSTRAP ROBUSTNESS REPORTING
    # ══════════════════════════════════════════════════════════════════════
    print("\n" + "═" * 76)
    print("P2b: HONEST BOOTSTRAP ROBUSTNESS REPORTING (Moderate Flaw #3)")
    print("═" * 76)

    s6_bmc = s6["rs6_1_bootstrap_mc_corrected"]
    s6_bpc = s6["rs6_1_bootstrap_permutation"]
    honest_bootstrap = honest_bootstrap_robustness_report(s6_bmc, s6_bpc)
    print(f"\n  Bootstrap MC p = {honest_bootstrap['bootstrap_mc_p']:.4f}")
    print(f"  Removed threshold: {honest_bootstrap['removed_threshold']}")
    print(f"  Revised label: {honest_bootstrap['revised_bootstrap_label']}")
    print(f"\n  PRIMARY METRIC: {honest_bootstrap['primary_robustness_metric']['result']}")
    print(f"  Verdict: {honest_bootstrap['primary_robustness_metric']['verdict']}")
    results["p2b_honest_bootstrap_robustness"] = honest_bootstrap

    # ══════════════════════════════════════════════════════════════════════
    # P3: R-3 k_eff-DEPENDENT CORRECTION
    # ══════════════════════════════════════════════════════════════════════
    print("\n" + "═" * 76)
    print("P3: R-3 k_eff-DEPENDENT CORRECTION f(k_eff) IN R₀ PARAMETRIZATION")
    print("  Model: R₀(k_eff, z) = A × k_eff^(-γ) × (1+z)^β")
    print("═" * 76)

    r3 = r3_keff_correction(loo_r0, surveys, beta_fixed)
    print(f"\n  Fit result: A = {r3['A_fit']:.2f}, γ = {r3['gamma_fit']:.3f}")
    print(f"  LOO-CV MAE: {r3['mae_sigma_r3']:.3f}σ")
    print(f"  Surveys |tension| < 1.5σ: {r3['n_lt15_sigma']}/5")
    print(f"  k_eff invariant CV: {r3['inv_fit_cv_pct']:.1f}%")
    print(f"\n  Per-survey LOO-CV tensions:")
    print(f"  {'Survey':<18}  {'k_eff':>6}  {'R₀_pred':>8}  {'R₀_S5':>8}  {'tension':>8}")
    print(f"  {'-'*18}  {'-'*6}  {'-'*8}  {'-'*8}  {'-'*8}")
    for name, v in r3["loo_cv_r3"].items():
        print(f"  {name:<18}  {v['k_eff']:>6.2f}  {v['r0_predicted']:>8.3f}  "
              f"{v['r0_loo_s5']:>8.3f}  {v['tension_sigma']:>+8.4f}σ")
    print(f"\n  {r3['interpretation']}")
    results["p3_r3_keff_correction"] = r3

    # ══════════════════════════════════════════════════════════════════════
    # REQUIREMENT STATUS UPDATE
    # ══════════════════════════════════════════════════════════════════════
    r6_ssot_pass = ssot_perm["pass_p_lt_005"]
    r3_pass = r3["r3_pass"]

    print("\n" + "═" * 76)
    print("SESSION 7 REQUIREMENT STATUS")
    print("═" * 76)
    print(f"  P1a (SSoT perm test): p={p_ssot:.4f} → {'✓ PASS' if r6_ssot_pass else '✗ FAIL'}")
    print(f"  P1b (baseline disclosure): ✓ COMPLETED")
    print(f"  P2a (β causal correction): ✓ COMPLETED")
    print(f"  P2b (Bootstrap honest reporting): ✓ COMPLETED")
    r3_status = "✓ < 1.5σ all" if r3_pass else f"{r3['n_lt15_sigma']}/5 < 1.5σ"
    print(f"  P3 (R-3 k_eff correction): MAE={r3['mae_sigma_r3']:.3f}σ, {r3_status}")

    summary = {
        "p1a_ssot_perm_p": float(p_ssot),
        "p1a_ssot_perm_pass": bool(r6_ssot_pass),
        "p1a_ssot_cv_pct": float(physical_cv_ssot),
        "p1b_bestfit_r_base": float(disclosure["r_base_bestfit"]),
        "p1b_r_base_deviation_from_ssot_pct": float(abs(disclosure["r_base_deviation_from_ssot_pct"])),
        "p1b_mean_dev_from_bestfit_pct": float(disclosure["mean_abs_deviation_from_bestfit_pct"]),
        "p2a_corrected_beta_causal": True,
        "p2b_bootstrap_threshold_removed": True,
        "p3_r3_mae_sigma": float(r3["mae_sigma_r3"]),
        "p3_r3_pass": bool(r3_pass),
        "p3_A_fit": float(r3["A_fit"]),
        "p3_gamma_fit": float(r3["gamma_fit"]),
        "p3_n_lt15_sigma": int(r3["n_lt15_sigma"]),
        "v24_requirements": {
            "R-1 (≥5 WL LOO-CV)":      "✓ Session 5",
            "R-2 (CMB z-growth model)": "✗ OPEN (out of scope Session 7)",
            "R-3 (k_eff CV < 10%)":     f"△ P3 ATTEMPT: inv_CV={r3['inv_fit_cv_pct']:.1f}%",
            "R-4' (Λ derivation)":      "✓ Session 6 CLOSED (Path B)",
            "R-5 (< 1σ all surveys)":   "✗ OPEN (structural limitation)",
            "R-6 (perm p < 0.05)":      (
                f"⚠️ REVISED: Session 5/6 p=0.0167 was best-fit quintuple. "
                f"SSoT-constrained p={p_ssot:.4f} ({'PASS' if r6_ssot_pass else 'FAIL'})"
            ),
        },
    }
    results["summary"] = summary

    # Save results
    out_path = str(BASE / "v24.0" / "data" / "section_7_session7_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n  Results saved to: data/section_7_session7_results.json")

    return results


if __name__ == "__main__":
    main()
