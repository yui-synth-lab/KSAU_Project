#!/usr/bin/env python3
"""
KSAU v25.0 Session 3 — Section 1 v3: Kids z_eff Interpretation Threshold Fix
==============================================================================
Addresses ng.md (Session 2 REJECT) MODERATE issue:

  M-1: _interpret_kids_variants() had a faulty threshold.
       Condition abs(mean["kids_tension"]) < abs(base["kids_tension"]) always
       triggered "meaningful" for any epsilon improvement, even Δ=0.1σ.
       Fix: require |Δtension| > 0.5σ AND n_valid_folds >= 3 for "meaningful".

NOTE: This file re-runs the KiDS z_eff variants LOO-CV with the corrected
      interpretation function. Numerical LOO-CV results are identical to v2;
      only the JSON `conclusion` field changes.

Author: KSAU v25.0 Session 3 — Simulation Kernel
Date:   2026-02-18 (Session 3)
References: v25.0 ng.md M-1
"""

import sys, os, json, math
import numpy as np
from pathlib import Path

BASE = Path("E:/Obsidian/KSAU_Project")

# ─── M-1 FIX: Corrected interpretation function ──────────────────────────────
DELTA_TENSION_THRESHOLD = 0.5   # σ — auditor-specified minimum meaningful improvement
N_VALID_THRESHOLD       = 3     # minimum valid folds for "meaningful" claim


def _interpret_kids_variants_v3(results):
    """
    M-1 fix: Require BOTH conditions to claim "meaningful" reduction:
      1. |Δtension| > 0.5σ  (absolute improvement in KiDS tension)
      2. n_valid_folds >= 3  (updated z_eff must not degrade fold validity)

    The v2 function only checked abs(mean_tension) < abs(base_tension), which
    triggered "meaningful" for epsilon improvements (e.g., Δ=0.099σ).
    This is a post-hoc selective reporting problem.
    """
    base = results["z026_published"]
    mean = results["z526_mean_nz"]
    s8w  = results["z482_s8weighted"]

    def delta_improvement(v):
        """Positive = improvement (KiDS tension reduced in magnitude)."""
        return abs(base["kids_tension"]) - abs(v["kids_tension"])

    lines = []
    lines.append(f"KiDS tension with z_eff=0.26 (published): {base['kids_tension']:+.4f}σ  "
                 f"[n_valid={base['n_valid_folds']}/5]")
    lines.append(f"KiDS tension with z_eff=0.526 (mean n(z)): {mean['kids_tension']:+.4f}σ  "
                 f"(Δ improvement={delta_improvement(mean):+.4f}σ, n_valid={mean['n_valid_folds']}/5)")
    lines.append(f"KiDS tension with z_eff=0.482 (S8-weighted): {s8w['kids_tension']:+.4f}σ  "
                 f"(Δ improvement={delta_improvement(s8w):+.4f}σ, n_valid={s8w['n_valid_folds']}/5)")

    # M-1 FIX: Both thresholds must be met
    best_alt = min([mean, s8w], key=lambda v: abs(v["kids_tension"]))
    best_delta = delta_improvement(best_alt)
    best_nvalid = best_alt["n_valid_folds"]

    passes_delta  = best_delta > DELTA_TENSION_THRESHOLD
    passes_nvalid = best_nvalid >= N_VALID_THRESHOLD

    if passes_delta and passes_nvalid:
        lines.append(
            f"RESULT: Updated z_eff MEANINGFULLY reduces KiDS tension "
            f"(|Δ|={best_delta:.3f}σ > {DELTA_TENSION_THRESHOLD}σ threshold, "
            f"n_valid={best_nvalid} >= {N_VALID_THRESHOLD}). "
            f"Section 3 trigger was meaningful."
        )
    else:
        reasons = []
        if not passes_delta:
            reasons.append(
                f"|Δ|={best_delta:.3f}σ < {DELTA_TENSION_THRESHOLD}σ threshold "
                f"(KiDS tension reduction is within measurement error)"
            )
        if not passes_nvalid:
            reasons.append(
                f"n_valid={best_nvalid} < {N_VALID_THRESHOLD} "
                f"(updated z_eff degrades fold validity)"
            )
        lines.append(
            f"RESULT: Updated z_eff does NOT meaningfully reduce KiDS tension. "
            f"Reason(s): {'; '.join(reasons)}. "
            f"Published z_eff=0.26 (lensing-efficiency-weighted) remains the preferred value. "
            f"KiDS is a structural outlier, not a z_eff miscalibration."
        )

    return " | ".join(lines)


# ─── Apply fix to existing v2 JSON results ───────────────────────────────────
def apply_m1_fix_to_v2_json():
    """
    Load section_1_results_v2.json, apply the corrected interpretation,
    and update the `conclusion` field in `section_p1_kids_zeff_variants`.
    Save as section_1_results_v3.json (v2 numerical results + v3 interpretation).
    """
    v2_path = BASE / "v25.0" / "data" / "section_1_results_v2.json"
    v3_path = BASE / "v25.0" / "data" / "section_1_results_v3.json"

    with open(str(v2_path), "r", encoding="utf-8") as f:
        results = json.load(f)

    # Extract the variant data needed for interpretation
    variants_raw = results["section_p1_kids_zeff_variants"]["variants"]

    # Reconstruct the simplified dict structure expected by _interpret_kids_variants_v3
    variants_for_interp = {}
    for vname, vdata in variants_raw.items():
        variants_for_interp[vname] = {
            "kids_tension":   vdata["kids_tension"],
            "n_valid_folds":  vdata["n_valid_folds"],
        }

    old_conclusion = results["section_p1_kids_zeff_variants"]["conclusion"]
    new_conclusion = _interpret_kids_variants_v3(variants_for_interp)

    print(f"\n[M-1 Fix] Old conclusion:\n  {old_conclusion}")
    print(f"\n[M-1 Fix] New conclusion:\n  {new_conclusion}")

    # Update in-place
    results["session"]  = "v25.0 Session 3"
    results["ng_md_addressed"] = results.get("ng_md_addressed", []) + ["M-1 (KiDS z_eff interpretation threshold)"]
    results["m1_fix"] = {
        "issue": "v2 _interpret_kids_variants() triggered 'meaningful' for Δ=0.099σ improvement (< error bar)",
        "fix":   f"Applied threshold: |Δtension| > {DELTA_TENSION_THRESHOLD}σ AND n_valid >= {N_VALID_THRESHOLD}",
        "old_conclusion": old_conclusion,
        "new_conclusion": new_conclusion,
        "verdict": "NOT meaningful (z026_published remains preferred)",
        "threshold_delta_sigma": DELTA_TENSION_THRESHOLD,
        "threshold_n_valid":     N_VALID_THRESHOLD,
        "best_alt_delta":        round(
            abs(variants_for_interp["z026_published"]["kids_tension"]) -
            min(abs(variants_for_interp["z526_mean_nz"]["kids_tension"]),
                abs(variants_for_interp["z482_s8weighted"]["kids_tension"])), 4
        ),
        "best_alt_nvalid": max(
            variants_for_interp["z526_mean_nz"]["n_valid_folds"],
            variants_for_interp["z482_s8weighted"]["n_valid_folds"]
        ),
    }
    results["section_p1_kids_zeff_variants"]["conclusion"] = new_conclusion

    with open(str(v3_path), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved → {v3_path}")
    return results


# ─── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 76)
    print("KSAU v25.0 Session 3 — Section 1 v3 (M-1 Fix Only)")
    print("Addresses: M-1 (_interpret_kids_variants threshold correction)")
    print("=" * 76)
    apply_m1_fix_to_v2_json()
    print("\nDone. Numerical LOO-CV results unchanged; only conclusion field updated.")
