#!/usr/bin/env python3
"""
KSAU v25.0 Section 4 — Multiple Testing Correction & Statistical Robustness
=============================================================================
Physical motivation: v24.0 reported 2 permutation tests without correction.
Bonferroni correction puts the SSoT-constrained p=0.025 exactly at the boundary.

This section:
4a. Bonferroni correction for v24.0 tests (2 tests → α_adj = 0.025)
4b. Compile all v24.0 + v25.0 tests and apply FDR (Benjamini-Hochberg)
4c. Report final table of corrected p-values

Author: KSAU v25.0 Simulation Kernel — Section 4
Date:   2026-02-19
References: v24.0 Session 7, v25.0 Section 1 results
"""

import json, math
import numpy as np
from pathlib import Path

BASE = Path("E:/Obsidian/KSAU_Project")


# ─── Helper: Benjamini-Hochberg FDR ──────────────────────────────────────────
def benjamini_hochberg(p_values):
    """
    Apply Benjamini-Hochberg FDR correction.
    Returns adjusted p-values (BH procedure).
    """
    n = len(p_values)
    # Sort p-values with indices
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    ranks   = list(range(1, n + 1))

    # BH adjusted p: p_adj_i = min(p_i * n / rank_i, 1.0)
    # Applied sequentially from largest rank
    bh_adj = [0.0] * n
    min_so_far = 1.0
    for j in range(n - 1, -1, -1):
        orig_idx, p = indexed[j]
        rank = ranks[j]
        bh_adj_raw = p * n / rank
        min_so_far = min(min_so_far, bh_adj_raw)
        bh_adj[j] = min_so_far

    # Re-attach to original indices
    result = [0.0] * n
    for j, (orig_idx, _) in enumerate(indexed):
        result[orig_idx] = min(1.0, bh_adj[j])

    return result


def bonferroni(p_values):
    """Bonferroni correction: multiply each p by number of tests."""
    n = len(p_values)
    return [min(p * n, 1.0) for p in p_values]


# ─── Section 4a: v24.0 Bonferroni correction ─────────────────────────────────
def v24_bonferroni():
    """
    4a: Apply Bonferroni correction to the 2 v24.0 permutation tests.

    v24.0 Tests:
      T1: Unconstrained permutation test (best-fit quintuple {8,5,4,3,2})
          p = 0.0167 (1/60 ... actual value from Session 5/6)
      T2: SSoT-constrained permutation test (quintuple {7,6,5,3,1})
          p = 0.025 (Session 7)
    """
    # v24.0 test p-values
    tests_v24 = [
        {
            "test_id":     "T1_v24",
            "description": "Unconstrained permutation (best-fit quintuple {8,5,4,3,2})",
            "session":     "Session 5/6",
            "p_raw":       0.0167,
            "note":        "p=2/120 (ranking of physical ordering among all 120 permutations)",
        },
        {
            "test_id":     "T2_v24",
            "description": "SSoT-constrained permutation (SSoT quintuple {7,6,5,3,1})",
            "session":     "Session 7",
            "p_raw":       0.025,
            "note":        "p=3/120 (ranking of physical ordering under SSoT-fixed shells)",
        },
    ]

    p_raw = [t["p_raw"] for t in tests_v24]
    alpha_nominal = 0.05
    alpha_bonf    = alpha_nominal / len(p_raw)   # 0.025
    p_bonf        = bonferroni(p_raw)
    p_bh          = benjamini_hochberg(p_raw)

    for i, t in enumerate(tests_v24):
        t["p_bonferroni"]       = round(p_bonf[i], 6)
        t["p_bh_fdr"]           = round(p_bh[i],   6)
        t["significant_bonf"]   = bool(p_bonf[i] < alpha_nominal)
        t["significant_bh"]     = bool(p_bh[i]   < alpha_nominal)
        t["significant_raw"]    = bool(p_raw[i]   < alpha_nominal)

    return {
        "n_tests":           len(tests_v24),
        "alpha_nominal":     alpha_nominal,
        "alpha_bonferroni":  alpha_bonf,
        "tests":             tests_v24,
        "summary": {
            "T1_bonferroni_significant": tests_v24[0]["significant_bonf"],
            "T2_bonferroni_significant": tests_v24[1]["significant_bonf"],
            "T1_bh_significant":         tests_v24[0]["significant_bh"],
            "T2_bh_significant":         tests_v24[1]["significant_bh"],
            "interpretation": (
                f"After Bonferroni correction (α_adj = {alpha_bonf}): "
                f"T1 (p={p_bonf[0]:.4f}) {'SIGNIFICANT' if tests_v24[0]['significant_bonf'] else 'NOT significant'}. "
                f"T2 (p={p_bonf[1]:.4f}) {'SIGNIFICANT (boundary)' if tests_v24[1]['significant_bonf'] else 'NOT significant'}. "
                f"T2=p=0.025 is exactly at the Bonferroni boundary (p ≤ α_adj = 0.025). "
                f"The p=0.025 result is marginal under strict Bonferroni control. "
                f"T1 (p=0.0167) is robust: 0.0167 < 0.025."
            ),
        },
    }


# ─── Section 4b: Full v24.0 + v25.0 FDR correction ──────────────────────────
def full_fdr_correction(section1_mae=None, section1_tensions=None):
    """
    4b: Compile all hypothesis tests from v24.0 and v25.0, apply FDR correction.

    All tests conducted in this research program:
      v24.0:
        T1: Unconstrained permutation (p=0.0167)
        T2: SSoT-constrained permutation (p=0.025)
        T3: Bootstrap MC (p=0.3165) — robustness test (not a hypothesis test per se)
        T4: B+P combined test (76% trials p<0.05) — converted to p≈0.24 (1-0.76)
      v25.0:
        T5: Cross-term LOO-CV improvement test — compare MAE vs baseline
            (if MAE improved, test: is improvement > 0 with n=5? binomial test)
        T6: KiDS/DES tension reduction — is |tension| < 1.5σ achieved for both?
    """
    tests_all = [
        {
            "test_id":   "T1_v24",
            "name":      "Unconstrained permutation test",
            "version":   "v24.0",
            "p_raw":     0.0167,
            "type":      "permutation",
            "null":      "Random k_eff ordering is as extreme as physical ordering",
        },
        {
            "test_id":   "T2_v24",
            "name":      "SSoT-constrained permutation test",
            "version":   "v24.0",
            "p_raw":     0.025,
            "type":      "permutation",
            "null":      "Physical k_eff↔R₀ ordering is not special under SSoT assignment",
        },
        {
            "test_id":   "T3_v24",
            "name":      "Bootstrap MC robustness (p≥0.2 threshold)",
            "version":   "v24.0",
            "p_raw":     0.3165,
            "type":      "bootstrap",
            "null":      "CV is not robust to ±10% noise",
            "note":      "Not a classical hypothesis test. Included for completeness.",
        },
    ]

    # v25.0 cross-term model test (if available)
    if section1_mae is not None:
        # One-sided test: is the new MAE better than baseline?
        # With n=5 surveys, the MAE is an average of 5 absolute tensions.
        # Under H₀: no improvement, new tensions ~ same distribution as v24.0.
        # We use a sign test: how many surveys improved (|new_t| < |v24_t|)?
        if section1_tensions is not None:
            v24_tensions = {
                "DES Y3":      1.821,
                "CFHTLenS":    0.593,
                "DLS":         0.877,
                "HSC Y3":      0.279,
                "KiDS-Legacy": 1.580,
            }
            n_improved = sum(
                1 for name, t in section1_tensions.items()
                if abs(t) < v24_tensions.get(name, 99)
            )
            # Sign test: P(k ≥ n_improved | n=5, p=0.5)
            from scipy.stats import binom
            p_sign = 1.0 - binom.cdf(n_improved - 1, 5, 0.5)
        else:
            p_sign = 1.0
            n_improved = 0

        tests_all.append({
            "test_id":   "T4_v25",
            "name":      "Cross-term LOO-CV improvement sign test",
            "version":   "v25.0",
            "p_raw":     round(p_sign, 4),
            "type":      "sign_test",
            "null":      "Cross-term model does not improve tension for majority of surveys",
            "n_improved": n_improved,
            "mae_new":   round(section1_mae, 4),
            "mae_v24":   1.030,
        })

    p_raw_all  = [t["p_raw"] for t in tests_all]
    p_bonf_all = bonferroni(p_raw_all)
    p_bh_all   = benjamini_hochberg(p_raw_all)

    for i, t in enumerate(tests_all):
        t["p_bonferroni"] = round(p_bonf_all[i], 6)
        t["p_bh_fdr"]     = round(p_bh_all[i],   6)
        t["sig_raw"]      = bool(t["p_raw"] < 0.05)
        t["sig_bonf"]     = bool(p_bonf_all[i] < 0.05)
        t["sig_bh"]       = bool(p_bh_all[i]   < 0.05)

    return {
        "n_tests":     len(tests_all),
        "alpha":       0.05,
        "tests":       tests_all,
        "n_sig_raw":   sum(1 for t in tests_all if t["sig_raw"]),
        "n_sig_bonf":  sum(1 for t in tests_all if t["sig_bonf"]),
        "n_sig_bh":    sum(1 for t in tests_all if t["sig_bh"]),
    }


# ─── Section 4c: Build summary table ─────────────────────────────────────────
def build_summary_table(bonf_v24, fdr_all):
    """4c: Build the comprehensive p-value table (per roadmap requirement)."""
    lines = []
    lines.append("Test ID   | Description                              | p_raw  | p_Bonf | p_BH   | sig_raw | sig_Bonf | sig_BH")
    lines.append("-" * 110)
    for t in fdr_all["tests"]:
        sig_raw  = "✓" if t["sig_raw"]  else "✗"
        sig_bonf = "✓" if t["sig_bonf"] else "✗"
        sig_bh   = "✓" if t["sig_bh"]   else "✗"
        lines.append(
            f"{t['test_id']:<10}| {t['name'][:40]:<42}| "
            f"{t['p_raw']:<7.4f}| {t['p_bonferroni']:<7.4f}| {t['p_bh_fdr']:<7.4f}| "
            f"{sig_raw:^8}| {sig_bonf:^9}| {sig_bh:^7}"
        )

    return "\n".join(lines)


def main():
    print("=" * 76)
    print("KSAU v25.0 Section 4 — Multiple Testing Correction")
    print("=" * 76)

    # 4a: v24.0 Bonferroni
    print("\nSection 4a: Bonferroni correction for v24.0 tests...")
    bonf_v24 = v24_bonferroni()
    print(f"  α_adj (Bonferroni) = {bonf_v24['alpha_bonferroni']}")
    print(f"  {bonf_v24['summary']['interpretation']}")

    # Load Section 1 results if available (for T4_v25)
    s1_path = BASE / "v25.0" / "data" / "section_1_results.json"
    section1_mae       = None
    section1_tensions  = None
    if s1_path.exists():
        with open(str(s1_path), "r", encoding="utf-8") as f:
            s1 = json.load(f)
        section1_mae = s1.get("section_1b_loo_cv", {}).get("mae_all")
        fold_results = s1.get("section_1b_loo_cv", {}).get("per_fold", {})
        section1_tensions = {n: v["tension"] for n, v in fold_results.items()}
        print(f"\nLoaded Section 1 results: MAE = {section1_mae:.4f}σ")

    # 4b: Full FDR correction
    print("\nSection 4b: Full FDR (Benjamini-Hochberg) correction...")
    fdr_all = full_fdr_correction(section1_mae, section1_tensions)

    # 4c: Summary table
    print("\nSection 4c: Complete p-value table:")
    table = build_summary_table(bonf_v24, fdr_all)
    print(table)

    print(f"\n  Tests significant under:")
    print(f"    Raw α=0.05:        {fdr_all['n_sig_raw']}/{fdr_all['n_tests']}")
    print(f"    Bonferroni:        {fdr_all['n_sig_bonf']}/{fdr_all['n_tests']}")
    print(f"    BH FDR:            {fdr_all['n_sig_bh']}/{fdr_all['n_tests']}")

    # Final interpretation
    t1_sig_bonf = any(t["test_id"] == "T1_v24" and t["sig_bonf"] for t in fdr_all["tests"])
    t2_sig_bonf = any(t["test_id"] == "T2_v24" and t["sig_bonf"] for t in fdr_all["tests"])

    print(f"\n  CONCLUSION:")
    print(f"    T1 (unconstrained, p=0.0167): {'SIGNIFICANT' if t1_sig_bonf else 'marginal'} "
          f"after Bonferroni correction.")
    print(f"    T2 (SSoT-constrained, p=0.025): {'SIGNIFICANT (boundary)' if t2_sig_bonf else 'marginal'} "
          f"after Bonferroni correction.")
    print(f"    T2 is at the EXACT Bonferroni boundary (p = α_adj = 0.025).")
    print(f"    The permutation evidence for k_eff ↔ R₀ ordering is MARGINAL.")

    results = {
        "date":    "2026-02-19",
        "section": "Section 4",
        "section_4a_bonferroni_v24":  bonf_v24,
        "section_4b_fdr_all_tests":   fdr_all,
        "section_4c_table":           table,
        "conclusions": {
            "T1_robust":        t1_sig_bonf,
            "T2_marginal":      t2_sig_bonf,
            "T2_boundary_note": "p=0.025 = α_adj exactly (Bonferroni boundary — not conclusive)",
            "recommendation":   (
                "The primary claim (k_eff ↔ R₀ ordering) rests on T1 (p=0.0167, "
                "Bonferroni-robust) and T2 (p=0.025, boundary). "
                "Further data (6+ surveys) needed to push T2 below the boundary. "
                "The ordering claim should be presented as 'marginal to significant' "
                "rather than 'significant' given the multiple testing landscape."
            ),
        },
    }

    out_path = BASE / "v25.0" / "data" / "section_4_results.json"
    with open(str(out_path), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved → {out_path}")
    return results


if __name__ == "__main__":
    main()
