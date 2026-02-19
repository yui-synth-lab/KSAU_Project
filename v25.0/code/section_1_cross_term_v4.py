#!/usr/bin/env python3
"""
KSAU v25.0 Session 4 — Section 1 v4: B-1 / M-NEW-1 / M-NEW-2 Fix
==================================================================
Addresses ng.md (Session 3 REJECT) issues:

  B-1 (BLOCKING): LOO-CV γ boundary solutions in 4/5 folds not recorded.
    - 3/5 folds (DES Y3, CFHTLenS, HSC Y3) have γ_loo = 0.001 (exact GAMMA_MIN)
    - 1/5 fold  (KiDS-Legacy)               has γ_loo = 0.0062 (quasi-boundary)
    - Only 1/5 fold (DLS) has well-identified γ_loo = 0.6195
    - This means the model effectively degenerates to 3-parameter form in 4/5 folds:
        R₀ = A × (1+z)^(β₀ + δβ ln k)  [because k^(-γ) ≈ 1 when γ→0]
    - Reported "4-parameter cross-term LOO-CV MAE = 1.3251σ" is INCORRECT;
      should be "effectively 3-parameter degenerate model LOO-CV MAE = 1.3251σ
      (γ non-identifiable in 4/5 folds)"
    Fix:
      1. Add gamma_boundary_flag to each fold entry
      2. Add beta0_boundary_flag to each fold entry (for M-NEW-2)
      3. Add b1_gamma_boundary_analysis summary to section_1b_loo_cv_v2
      4. Add mae_description_b1_corrected note
      5. Confirm Section 1 negative conclusion unchanged (strengthened)

  M-NEW-1 (MODERATE): best_alt_nvalid = 3 is incorrect.
    - In _interpret_kids_variants_v3(), best_alt = min([z526, z482], key=|tension|)
        z526 |tension| = 2.924, z482 |tension| = 2.9986 → best_alt = z526
    - z526 n_valid_folds = 2, therefore best_alt_nvalid should be 2 (not 3)
    - The v3 code computed max(z526_nvalid=2, z482_nvalid=3) = 3, which is wrong
    Fix: correct m1_fix.best_alt_nvalid from 3 → 2

  M-NEW-2 (MODERATE): DLS fold β₀_loo = -5.0 = BETA0_MIN (boundary) not detected.
    - DLS beta0_loo = -5.0 = exact lower bound (BETA0_MIN = -5.0)
    - sanity_valid was True → incorrect (boundary solution ≠ identified solution)
    Fix:
      1. Add beta0_boundary_flag = True to DLS fold
      2. Add boundary issue to DLS sanity_issues
      3. Override DLS sanity_valid to False

Author: KSAU v25.0 Session 4 — Simulation Kernel
Date:   2026-02-18 (Session 4)
References: v25.0 ng.md B-1, M-NEW-1, M-NEW-2
"""

import copy
import json
from pathlib import Path

BASE = Path("E:/Obsidian/KSAU_Project")
V3_PATH = BASE / "v25.0" / "data" / "section_1_results_v3.json"
V4_PATH = BASE / "v25.0" / "data" / "section_1_results_v4.json"

# Physical constraint bounds — must match section_1_cross_term_v2.py
GAMMA_MIN  = 0.001
GAMMA_MAX  = 2.0
BETA0_MIN  = -5.0
BETA0_MAX  = 10.0

# B-1 analysis thresholds
GAMMA_EXACT_BOUNDARY_TOL = 1e-9        # γ_loo ≈ GAMMA_MIN
GAMMA_BOUNDARY_THRESHOLD = 0.01        # quasi-boundary; captures KiDS-Legacy 0.0062
BETA0_EXACT_BOUNDARY_TOL = 1e-9        # β₀_loo ≈ BETA0_MIN


# ─── Helper: boundary detection ──────────────────────────────────────────────

def check_gamma_boundary(gamma_loo):
    """
    Returns (is_boundary: bool, is_exact: bool, flag_msg: str or None)
    is_boundary = True  if γ_loo ≤ GAMMA_BOUNDARY_THRESHOLD
    is_exact    = True  if γ_loo == GAMMA_MIN (within tolerance)
    """
    is_exact = abs(gamma_loo - GAMMA_MIN) < GAMMA_EXACT_BOUNDARY_TOL
    is_quasi = (gamma_loo <= GAMMA_BOUNDARY_THRESHOLD) and not is_exact
    is_boundary = is_exact or is_quasi

    if is_exact:
        msg = (
            f"gamma_loo={gamma_loo} at lower bound GAMMA_MIN={GAMMA_MIN} "
            f"[B-1: model degenerates to 3-parameter: A*(1+z)^(β₀+δβ ln k); "
            f"k^(-γ)≈1, k_eff-scaling absent]"
        )
    elif is_quasi:
        msg = (
            f"gamma_loo={gamma_loo} quasi-boundary "
            f"(< γ_threshold={GAMMA_BOUNDARY_THRESHOLD}; k_eff-scaling effectively absent) "
            f"[B-1: effectively 3-parameter degenerate]"
        )
    else:
        msg = None

    return is_boundary, is_exact, msg


def check_beta0_boundary(beta0_loo):
    """
    Returns (is_boundary: bool, flag_msg: str or None)
    is_boundary = True  if β₀_loo == BETA0_MIN (within tolerance)
    """
    is_at_bound = abs(beta0_loo - BETA0_MIN) < BETA0_EXACT_BOUNDARY_TOL
    if is_at_bound:
        msg = (
            f"beta0_loo={beta0_loo} at lower bound BETA0_MIN={BETA0_MIN} "
            f"[M-NEW-2: β₀ non-identifiable; optimizer wants β₀ < {BETA0_MIN} "
            f"but is constrained — β₀ boundary solution, not a valid fit]"
        )
    else:
        msg = None
    return is_at_bound, msg


# ─── Apply boundary flags to a single fold dict ───────────────────────────────

def apply_boundary_flags(fold_name, fold_data):
    """
    Apply B-1 (γ boundary) and M-NEW-2 (β₀ boundary) flags to one fold.
    Returns a deep-copied, updated fold dict.
    """
    fd = copy.deepcopy(fold_data)

    # --- B-1: γ boundary ---
    gamma_loo = fd["gamma_loo"]
    gamma_bd, gamma_exact, gamma_msg = check_gamma_boundary(gamma_loo)
    fd["gamma_boundary_flag"] = gamma_bd
    fd["gamma_at_exact_lower_bound"] = gamma_exact
    if gamma_bd and gamma_msg:
        if gamma_msg not in fd.get("sanity_issues", []):
            fd.setdefault("sanity_issues", []).insert(0, gamma_msg)

    # --- M-NEW-2: β₀ boundary ---
    beta0_loo = fd["beta0_loo"]
    beta0_bd, beta0_msg = check_beta0_boundary(beta0_loo)
    fd["beta0_boundary_flag"] = beta0_bd
    if beta0_bd:
        if beta0_msg and beta0_msg not in fd.get("sanity_issues", []):
            fd.setdefault("sanity_issues", []).append(beta0_msg)
        # M-NEW-2: override sanity_valid → False
        if fd.get("sanity_valid", True):
            fd["sanity_valid"] = False
            fd.setdefault("sanity_override_notes", []).append(
                f"[M-NEW-2 fix] sanity_valid overridden False: "
                f"beta0_loo={beta0_loo} == BETA0_MIN={BETA0_MIN} (boundary, non-identified)"
            )

    return fd


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 76)
    print("KSAU v25.0 Session 4 — Section 1 v4 (B-1 / M-NEW-1 / M-NEW-2 Fix)")
    print("=" * 76)

    with open(str(V3_PATH), "r", encoding="utf-8") as f:
        results = json.load(f)

    # ─── B-1 + M-NEW-2: Apply boundary flags to main section_1b_loo_cv_v2 ────

    loo_cv = results["section_1b_loo_cv_v2"]
    per_fold = loo_cv["per_fold"]

    folds_gamma_exact = []
    folds_gamma_quasi = []
    folds_beta0_bound = []

    print("\n[B-1 + M-NEW-2] Applying boundary flags to main LOO-CV per_fold...")
    for fold_name in list(per_fold.keys()):
        fd_orig = per_fold[fold_name]
        fd_fixed = apply_boundary_flags(fold_name, fd_orig)
        per_fold[fold_name] = fd_fixed

        if fd_fixed["gamma_at_exact_lower_bound"]:
            folds_gamma_exact.append(fold_name)
        elif fd_fixed["gamma_boundary_flag"]:
            folds_gamma_quasi.append(fold_name)

        if fd_fixed["beta0_boundary_flag"]:
            folds_beta0_bound.append(fold_name)

        print(f"  {fold_name:<15}: γ={fd_fixed['gamma_loo']:.4f}  "
              f"γ_bd={fd_fixed['gamma_boundary_flag']}  "
              f"β₀={fd_fixed['beta0_loo']:.4f}  "
              f"β₀_bd={fd_fixed['beta0_boundary_flag']}  "
              f"sanity_valid={fd_fixed['sanity_valid']}")

    all_gamma_boundary = folds_gamma_exact + folds_gamma_quasi
    n_gamma_bd = len(all_gamma_boundary)

    # Add B-1 summary block
    loo_cv["b1_gamma_boundary_analysis"] = {
        "gamma_min_constraint": GAMMA_MIN,
        "gamma_boundary_threshold": GAMMA_BOUNDARY_THRESHOLD,
        "folds_at_exact_gamma_lower_bound": folds_gamma_exact,
        "folds_at_quasi_gamma_boundary": folds_gamma_quasi,
        "all_gamma_boundary_folds": all_gamma_boundary,
        "n_gamma_boundary_folds": n_gamma_bd,
        "n_total_folds": 5,
        "fraction_gamma_boundary": n_gamma_bd / 5,
        "structural_failure_note": (
            f"B-1 (BLOCKING): {n_gamma_bd}/5 LOO-CV folds have γ→0 boundary convergence. "
            f"Exact boundary (γ={GAMMA_MIN}): {folds_gamma_exact} ({len(folds_gamma_exact)}/5). "
            f"Quasi-boundary (γ < {GAMMA_BOUNDARY_THRESHOLD}): {folds_gamma_quasi} ({len(folds_gamma_quasi)}/5). "
            f"Only 1 fold (DLS, γ=0.6195) has an identified γ parameter. "
            f"In {n_gamma_bd}/5 folds the model degenerates to "
            f"R₀ = A × (1+z)^(β₀+δβ ln k) [3-parameter form]. "
            f"This is the same structural failure class as P-NEW-3 "
            f"(M0 global fit γ→0+, recorded in Session 3). "
            f"The LOO-CV is NOT validating a 4-parameter cross-term model in {n_gamma_bd}/5 folds."
        ),
    }

    # Add corrected MAE description
    loo_cv["mae_description_b1_corrected"] = (
        f"LOO-CV MAE = 1.3251σ (all 5 folds) is the MAE of an "
        f"EFFECTIVELY 3-PARAMETER DEGENERATE MODEL in {n_gamma_bd}/5 folds. "
        f"Previous description ('4パラメータ cross-term モデルの LOO-CV MAE = 1.3251σ') "
        f"is corrected to: "
        f"'実質3パラメータ縮退モデルの LOO-CV MAE = 1.3251σ ({n_gamma_bd}/5 fold で γ 非識別)'. "
        f"AIC/BIC漸近正規性はγ境界解では成立しない (P-NEW-3論理と同一)。"
    )

    print(f"\n  γ-exact boundary folds ({len(folds_gamma_exact)}/5): {folds_gamma_exact}")
    print(f"  γ-quasi boundary folds ({len(folds_gamma_quasi)}/5): {folds_gamma_quasi}")
    print(f"  β₀ boundary folds ({len(folds_beta0_bound)}/5): {folds_beta0_bound}")

    # ─── M-NEW-2: Recount valid/degen folds after DLS override ───────────────

    new_valid = [fn for fn, fd in per_fold.items() if fd["sanity_valid"]]
    new_degen = [fn for fn, fd in per_fold.items() if not fd["sanity_valid"]]

    old_n_valid = loo_cv["n_valid_folds"]
    loo_cv["n_valid_folds"] = len(new_valid)
    loo_cv["n_degen_folds"] = len(new_degen)
    loo_cv["valid_fold_names"] = new_valid
    loo_cv["degen_fold_names"] = new_degen

    # Recompute valid-only MAE
    valid_tensions = [abs(per_fold[fn]["tension"]) for fn in new_valid]
    new_mae_valid = sum(valid_tensions) / len(valid_tensions) if valid_tensions else 0.0
    loo_cv["mae_valid_folds"] = round(new_mae_valid, 4)
    loo_cv["mae_valid_note"] = (
        f"[M-NEW-2 fix] n_valid: {old_n_valid} → {len(new_valid)}. "
        f"DLS fold sanity_valid overridden to False (β₀_loo={BETA0_MIN} boundary). "
        f"Valid folds: {new_valid}. "
        f"New MAE (valid only): {new_mae_valid:.4f}σ."
    )

    print(f"\n  [M-NEW-2] Valid fold count: {old_n_valid} → {len(new_valid)}")
    print(f"  Valid: {new_valid}")
    print(f"  Degen: {new_degen}")
    print(f"  New MAE (valid): {new_mae_valid:.4f}σ")

    # ─── Also apply boundary flags to kids_zeff_variants per_fold ────────────

    kids_variants = results["section_p1_kids_zeff_variants"]["variants"]
    for vname, vdata in kids_variants.items():
        if "per_fold" in vdata:
            for fn in list(vdata["per_fold"].keys()):
                vdata["per_fold"][fn] = apply_boundary_flags(fn, vdata["per_fold"][fn])

    # ─── M-NEW-1: Fix best_alt_nvalid ────────────────────────────────────────

    m1 = results["m1_fix"]
    old_nvalid = m1["best_alt_nvalid"]

    # Recompute: best_alt = min([z526, z482], key=|tension|)
    z526_tension = abs(kids_variants["z526_mean_nz"]["kids_tension"])
    z482_tension = abs(kids_variants["z482_s8weighted"]["kids_tension"])
    z526_nvalid  = kids_variants["z526_mean_nz"]["n_valid_folds"]
    z482_nvalid  = kids_variants["z482_s8weighted"]["n_valid_folds"]

    if z526_tension <= z482_tension:
        best_alt_name    = "z526_mean_nz"
        correct_nvalid   = z526_nvalid
        best_alt_tension = z526_tension
    else:
        best_alt_name    = "z482_s8weighted"
        correct_nvalid   = z482_nvalid
        best_alt_tension = z482_tension

    m1["best_alt_nvalid"] = correct_nvalid
    m1["m_new1_fix"] = {
        "issue": (
            f"v3 code computed best_alt_nvalid = max(z526_nvalid={z526_nvalid}, "
            f"z482_nvalid={z482_nvalid}) = {old_nvalid}. "
            f"This is inconsistent with _interpret_kids_variants_v3() which selects "
            f"best_alt = min([z526, z482], key=|tension|)."
        ),
        "fix": (
            f"best_alt = {best_alt_name} "
            f"(|tension|={best_alt_tension:.4f} = min of two variants). "
            f"best_alt_nvalid = {best_alt_name}.n_valid_folds = {correct_nvalid}."
        ),
        "old_value": old_nvalid,
        "new_value": correct_nvalid,
        "z526_tension": round(z526_tension, 4),
        "z482_tension": round(z482_tension, 4),
        "z526_nvalid":  z526_nvalid,
        "z482_nvalid":  z482_nvalid,
    }

    print(f"\n  [M-NEW-1] best_alt_nvalid: {old_nvalid} → {correct_nvalid}")
    print(f"  best_alt = {best_alt_name} (|tension|={best_alt_tension:.4f})")

    # ─── Update session metadata ──────────────────────────────────────────────

    results["session"] = "v25.0 Session 4"
    results["ng_md_addressed"] = results.get("ng_md_addressed", []) + [
        "B-1 (LOO-CV γ boundary 4/5 folds — structural failure formally recorded)",
        "M-NEW-1 (best_alt_nvalid corrected: 3 → 2)",
        "M-NEW-2 (DLS fold β₀ boundary: sanity_valid overridden to False)",
    ]

    # ─── Final confirmed conclusion (B-1 strengthens negative result) ─────────

    results["section_1_final_conclusion_b1_confirmed"] = {
        "dual_structural_failure": (
            "The v25.0 Section 1 cross-term model exhibits a DUAL structural failure: "
            "(A) Over-fitting: 4 params / 5 data points (dof_ratio=0.80); "
            f"(B) γ non-identifiability: {n_gamma_bd}/5 LOO-CV folds converge to "
            f"γ→0 boundary — model reduces to 3-parameter form in {n_gamma_bd}/5 folds. "
            "This dual failure was missed in Sessions 1-3 (only failure A was noted). "
            "B-1 fix confirms and deepens the negative result."
        ),
        "corrected_narrative": (
            "v25.0 主要否定的結果（修正版）: "
            "v23.0 エンジンの4パラメータ cross-term モデルは、"
            f"(1) 5データ/4パラメータの過適合、および "
            f"(2) γ の非識別性（{n_gamma_bd}/5 fold で γ→0 収束、モデルが実質3パラメータに縮退）"
            "という二重の構造的失敗により、v24.0 より悪い MAE=1.3251σ を示した。"
            "これは v23.0 エンジン刷新（v26.0）の科学的根拠を確立する重要な否定的結果である。"
        ),
        "conclusion_unchanged": (
            "Section 1 の最終結論（cross-term モデルの否定的結果）は B-1 修正後も変わらない。"
            "B-1 はその失敗の構造的根拠をより正確に記述するものであり、結論を覆すものではない。"
        ),
    }

    # ─── Save v4 ──────────────────────────────────────────────────────────────

    with open(str(V4_PATH), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n[DONE] Results saved → {V4_PATH}")
    print("\nSummary of fixes applied:")
    print(f"  B-1  : γ boundary flags added; {n_gamma_bd}/5 folds flagged; "
          f"structural failure note added; MAE description corrected.")
    print(f"  M-NEW-2: DLS fold sanity_valid → False (β₀_loo={BETA0_MIN} boundary)")
    print(f"  M-NEW-1: best_alt_nvalid {old_nvalid} → {correct_nvalid}")


if __name__ == "__main__":
    main()
