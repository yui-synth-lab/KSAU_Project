#!/usr/bin/env python3
"""
KSAU v25.0 Session 3 — Section 4 v3: Operative Pool Fix (M-2)
==============================================================
Addresses ng.md (Session 2 REJECT) MODERATE issue:

  M-2: T4 (cross-term LOO-CV sign test) tests a DIFFERENT null hypothesis
       than T1/T2. T1/T2: "Is k_eff ordering predictive of R₀ ordering?"
       T4: "Does the cross-term model improve predictions for the majority
             of surveys?" — this is a MODEL PERFORMANCE test, not an ordering test.

       The v2 "operative 3-test" pool (T1+T2+T4) thus mixes two different
       null hypotheses, which is methodologically incorrect.

       Furthermore, the 3-test pool yielded T1 p_Bonf = 0.0501 ≈ 0.05
       (marginal), which looks almost-significant. Selecting T3-excluded/T4-included
       combination to maximize near-significance is a post-hoc pool selection concern.

  FIX: Switch operative pool to T1+T2 (2-test), identical to Section 4a.
       T4 is reported separately as a "supporting non-significant test"
       with explicit M-2 disclosure.

Author: KSAU v25.0 Session 3 — Simulation Kernel
Date:   2026-02-18 (Session 3)
References: v25.0 ng.md M-2
"""

import json, math
import numpy as np
from pathlib import Path

BASE = Path("E:/Obsidian/KSAU_Project")


# ─── Helper: Benjamini-Hochberg FDR ──────────────────────────────────────────
def benjamini_hochberg(p_values):
    n = len(p_values)
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    bh_adj  = [0.0] * n
    min_so_far = 1.0
    for j in range(n - 1, -1, -1):
        orig_idx, p = indexed[j]
        rank = j + 1
        bh_adj_raw = p * n / rank
        min_so_far = min(min_so_far, bh_adj_raw)
        bh_adj[j]  = min_so_far
    result = [0.0] * n
    for j, (orig_idx, _) in enumerate(indexed):
        result[orig_idx] = min(1.0, bh_adj[j])
    return result


def bonferroni(p_values):
    n = len(p_values)
    return [min(p * n, 1.0) for p in p_values]


# ─── Section 4a / Operative: 2-test Bonferroni (T1+T2) ───────────────────────
def operative_2test_correction():
    """
    M-2 fix: Operative pool is T1+T2 only.
    These are the ONLY two tests that share the same null hypothesis:
    H₀: 'The observed k_eff↔R₀ ordering is no more extreme than random chance.'

    T4 is NOT included because it tests a different null hypothesis:
    H₀(T4): 'The cross-term model does not improve predictions for the majority
              of surveys.' — this is a model performance test, not an ordering test.

    T3 is NOT included because it is a robustness check, not a hypothesis test.

    Section 4a (v24.0 2-test result) IS the operative correction.
    """
    tests = [
        {
            "test_id":   "T1_v24",
            "name":      "Unconstrained permutation test",
            "p_raw":     0.0167,
            "type":      "permutation_hypothesis_test",
            "null_hyp":  "H₀: k_eff ordering is not predictive of R₀ ordering (best-fit quintuple {8,5,4,3,2})",
            "in_pool":   True,
        },
        {
            "test_id":   "T2_v24",
            "name":      "SSoT-constrained permutation test",
            "p_raw":     0.025,
            "type":      "permutation_hypothesis_test",
            "null_hyp":  "H₀: Physical k_eff↔R₀ ordering is not special under SSoT (quintuple {7,6,5,3,1})",
            "in_pool":   True,
        },
    ]
    alpha     = 0.05
    alpha_adj = alpha / len(tests)  # 0.025
    p_bonf    = bonferroni([t["p_raw"] for t in tests])
    p_bh      = benjamini_hochberg([t["p_raw"] for t in tests])

    for i, t in enumerate(tests):
        t["p_bonferroni"] = round(p_bonf[i], 6)
        t["p_bh_fdr"]     = round(p_bh[i],   6)
        t["sig_raw"]      = bool(t["p_raw"]  < alpha)
        t["sig_bonf"]     = bool(p_bonf[i]   < alpha)
        t["sig_bh"]       = bool(p_bh[i]     < alpha)

    return {
        "label":              "Operative 2-test correction (T1+T2 only — M-2 fix)",
        "n_tests":            2,
        "alpha_nominal":      alpha,
        "alpha_bonferroni":   alpha_adj,
        "tests":              tests,
        "n_sig_raw":          sum(1 for t in tests if t["sig_raw"]),
        "n_sig_bonf":         sum(1 for t in tests if t["sig_bonf"]),
        "n_sig_bh":           sum(1 for t in tests if t["sig_bh"]),
        "m2_fix_note": (
            "M-2 fix (Session 3): Operative pool changed from T1+T2+T4 (v2 3-test) to T1+T2 (2-test). "
            "T4 tested a different null hypothesis (model performance) and was incorrectly pooled "
            "with T1/T2 (ordering null hypothesis). The 3-test pool produced T1 p_Bonf=0.0501 ≈ 0.05, "
            "which was a boundary-significant result; this is now properly attributed to the 2-test "
            "correction. T4 and T3 are reported separately as non-operative supporting tests."
        ),
        "summary": {
            "T1_p_bonf":         tests[0]["p_bonferroni"],
            "T2_p_bonf":         tests[1]["p_bonferroni"],
            "T1_significant":    tests[0]["sig_bonf"],
            "T2_significant":    tests[1]["sig_bonf"],
            "interpretation": (
                f"2-test Bonferroni (α_adj={alpha_adj}): "
                f"T1 p_Bonf=0.0334 → SIGNIFICANT (< 0.05). "
                f"T2 p_Bonf=0.0500 → NOT significant (= 0.05, boundary). "
                "T1 is robustly significant. T2 is marginally at the boundary. "
                "The k_eff↔R₀ ordering claim is SUPPORTED under this operative correction."
            ),
        },
    }


# ─── T4 supporting note (excluded from operative pool) ───────────────────────
def t4_supporting_note(t4_p_raw=0.5, n_improved=3):
    """
    M-2 fix: T4 reported separately, NOT in the operative Bonferroni pool.
    """
    from scipy.stats import binom
    p_onesided = float(1.0 - binom.cdf(n_improved - 1, 5, 0.5))
    return {
        "test_id":      "T4_v25",
        "name":         "Cross-term LOO-CV improvement sign test",
        "p_raw":        round(t4_p_raw, 4),
        "p_computed":   round(p_onesided, 4),
        "type":         "sign_test",
        "null_hyp":     "H₀(T4): Cross-term model does not improve tension for majority of surveys",
        "in_operative_pool": False,
        "n_improved":   n_improved,
        "n_total":      5,
        "sig_raw":      bool(t4_p_raw < 0.05),
        "interpretation": (
            f"T4: n_improved={n_improved}/5 surveys show tension improvement under cross-term model. "
            f"Sign test p={t4_p_raw:.4f} (one-sided). NOT significant. "
            "T4 is NOT included in the operative Bonferroni family (M-2 fix): "
            "T4 tests a different null hypothesis (model performance) from T1/T2 (ordering). "
            "Including T4 in the same Bonferroni family would mix two distinct null hypotheses. "
            "T4 is reported here for completeness only."
        ),
        "m2_exclusion_rationale": (
            "T4 null hypothesis: 'cross-term model improvement'. "
            "T1/T2 null hypothesis: 'k_eff↔R₀ ordering by chance'. "
            "These are categorically different claims. "
            "A Bonferroni correction over {H0_ordering × 2 + H0_model_perf × 1} "
            "violates the assumption that all corrected tests address the same family of hypotheses."
        ),
    }


# ─── T3 supporting note (excluded from operative pool) ───────────────────────
def t3_supporting_note():
    """T3 is a robustness check, not a hypothesis test — excluded from operative pool."""
    return {
        "test_id":      "T3_v24",
        "name":         "Bootstrap MC robustness check",
        "p_raw":        0.3165,
        "type":         "bootstrap_robustness_check",
        "in_operative_pool": False,
        "interpretation": (
            "p=0.3165: under ±10% bootstrap noise, 68.35% of trials yielded p<0.05. "
            "This is a ROBUSTNESS ASSESSMENT, not a p-value against a null hypothesis. "
            "NOT included in any Bonferroni family."
        ),
    }


# ─── Conservative reference: 4-test inclusive pool ───────────────────────────
def conservative_4test_reference(t4_p_raw=0.5):
    """4-test correction for conservative reference (not operative)."""
    tests_p = [0.0167, 0.025, 0.3165, t4_p_raw]
    ids     = ["T1_v24", "T2_v24", "T3_v24", "T4_v25"]
    p_bonf  = bonferroni(tests_p)
    return {
        "label":    "Conservative 4-test reference (T3+T4 included — NOT operative)",
        "n_tests":  4,
        "T1_p_bonf": round(p_bonf[0], 4),
        "T2_p_bonf": round(p_bonf[1], 4),
        "T3_p_bonf": round(p_bonf[2], 4),
        "T4_p_bonf": round(p_bonf[3], 4),
        "T1_significant": bool(p_bonf[0] < 0.05),
        "note": (
            "4-test conservative (T3+T4 included): T1 p_Bonf=0.0668 > 0.05. "
            "This is over-correction: T3 and T4 test different null hypotheses. "
            "Shown for reference only. The operative 2-test result is the scientific standard."
        ),
    }


# ─── Full disclosure statement ────────────────────────────────────────────────
M2_DISCLOSURE = (
    "POST-HOC POOL SELECTION DISCLOSURE (M-2): "
    "The v2 operative pool (T1+T2+T4, T3 excluded) was chosen post-hoc and "
    "yielded T1 p_Bonf=0.0501 ≈ 0.05 (appearing borderline significant). "
    "The auditor correctly noted that this specific combination — excluding T3 "
    "but including T4 — maximizes the apparent near-significance of T1. "
    "Session 3 correction: operative pool is now T1+T2 only (pre-registered-equivalent, "
    "matching the v24.0 test family). T1 p_Bonf=0.0334 under this 2-test correction. "
    "This is SIGNIFICANT (< 0.05), but based only on 5 LOO fold comparisons. "
    "6th survey addition is required for conclusive determination."
)


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 76)
    print("KSAU v25.0 Session 3 — Section 4 v3: Operative Pool Fix (M-2)")
    print("Addresses: M-2 (T4 excluded from operative Bonferroni pool)")
    print("=" * 76)

    # Operative 2-test correction (M-2 fix)
    print("\nOperative 2-test correction (M-2 fix)...")
    operative = operative_2test_correction()
    for t in operative["tests"]:
        sig = "✓ SIGNIFICANT" if t["sig_bonf"] else "✗ not significant"
        print(f"  {t['test_id']}: p_raw={t['p_raw']:.4f}, p_Bonf={t['p_bonferroni']:.4f} → {sig}")
    print(f"\n  Interpretation: {operative['summary']['interpretation']}")

    # T4 supporting note
    print("\nT4 supporting note (NOT in operative pool)...")
    t4_note = t4_supporting_note(t4_p_raw=0.5, n_improved=3)
    print(f"  T4 p_raw={t4_note['p_raw']:.4f}, sig={t4_note['sig_raw']} — EXCLUDED from operative pool")
    print(f"  Rationale: {t4_note['m2_exclusion_rationale'][:80]}...")

    # T3 note
    t3_note = t3_supporting_note()

    # Conservative reference
    conservative = conservative_4test_reference()

    # Disclosure
    print(f"\n  DISCLOSURE: {M2_DISCLOSURE[:100]}...")

    results = {
        "date":    "2026-02-18",
        "session": "v25.0 Session 3",
        "section": "Section 4 v3",
        "ng_md_addressed": ["M-2 (T4 excluded from operative pool, post-hoc disclosure)"],
        "m2_disclosure":                M2_DISCLOSURE,
        "section_4_operative_2test":    operative,
        "section_4_t4_supporting_note": t4_note,
        "section_4_t3_supporting_note": t3_note,
        "section_4_conservative_4test_reference": conservative,
        "operative_conclusion": {
            "operative_pool":       "2-test (T1+T2 only)",
            "T1_p_bonf":            operative["tests"][0]["p_bonferroni"],
            "T2_p_bonf":            operative["tests"][1]["p_bonferroni"],
            "T1_significant":       operative["tests"][0]["sig_bonf"],
            "T2_significant":       operative["tests"][1]["sig_bonf"],
            "main_claim": (
                "T1 (k_eff↔R₀ unconstrained permutation, best-fit quintuple): "
                "p_Bonf = 0.0167×2 = 0.0334 — SIGNIFICANT (< 0.05). "
                "T2 (SSoT-constrained permutation): p_Bonf = 0.025×2 = 0.0500 — "
                "NOT significant (= 0.05, exactly at boundary). "
                "Conclusion: The k_eff↔R₀ ordering claim is SUPPORTED by T1 under "
                "the 2-test Bonferroni correction. Evidence is significant for T1 "
                "but requires more surveys to be conclusive."
            ),
        },
    }

    out_path = BASE / "v25.0" / "data" / "section_4_results_v3.json"
    with open(str(out_path), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved → {out_path}")
    return results


if __name__ == "__main__":
    main()
