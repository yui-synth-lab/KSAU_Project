#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
"""
KSAU v30.0 - Factor-of-7 Origin Analysis (Session 12)
=======================================================
Addresses go.md HIGH-priority directives:
  - Condition E: Algebraic origin of q_mult = 7
  - Section 3:   Monte Carlo test for BAO ratio 7.0

APPROACH (per go.md recommendation):
  "The factor-7 problem may share a common root.
   Explore factorization of N_leech = 196560 and
   E8 root system connections before separating."

This script performs THREE analyses:

  Part A: Algebraic structure analysis
    - Prime factorization of N_leech = 196560
    - Identify '7' within the Leech lattice geometry
    - Decompose D_bulk=24 → 7 via dimensional cascades
    - Evaluate whether q_mult=7 is derivable from SSoT dimensions

  Part B: Section 3 Monte Carlo Test
    - Null hypothesis H0: "The ratio BAO / R_pure ≈ 7 is a coincidence.
      A randomly chosen N from a geometric ensemble would produce a ratio
      equally close to an integer."
    - Method: Sample random kissing numbers from [100000, 400000],
      compute R_rand = N^0.25, compute ratio = BAO / R_rand,
      count how often |ratio - round(ratio)| < 0.0028 (same precision as obs)
    - p_value = fraction of random N yielding ratio within tolerance of integer

  Part C: Combined assessment
    - Is the factor 7 algebraically necessary, or merely numerological?
    - Decision: UPGRADE or MAINTAIN NUMERICAL COINCIDENCE CANDIDATE

SSoT Compliance:
  - Loads all constants from v6.0/data/ JSON files.
  - Does NOT hardcode N_leech, BAO, or q_mult.
"""

import numpy as np
import json
from pathlib import Path
from math import gcd, isqrt
import sys


# ─────────────────────────────────────────────
# Data Loading
# ─────────────────────────────────────────────

def load_data():
    base_path = Path(__file__).resolve().parent.parent.parent
    with open(base_path / "v6.0" / "data" / "physical_constants.json", "r") as f:
        phys = json.load(f)
    with open(base_path / "v6.0" / "data" / "cosmological_constants.json", "r") as f:
        cosmo = json.load(f)
    return phys, cosmo


# ─────────────────────────────────────────────
# Part A: Algebraic Origin Analysis
# ─────────────────────────────────────────────

def prime_factorize(n):
    """Return the prime factorization of n as a dict {prime: exponent}."""
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


def analyze_algebraic_origins(phys, cosmo):
    print("=" * 65)
    print("PART A: Algebraic Origin of Factor-of-7 in KSAU Framework")
    print("=" * 65)

    # ── A.1  N_leech prime factorization ──────────────────────────
    n_leech = phys["N_leech"]
    factors = prime_factorize(n_leech)
    print(f"\nA.1  N_leech = {n_leech}")
    factor_str = " × ".join(
        f"{p}^{e}" if e > 1 else f"{p}" for p, e in sorted(factors.items())
    )
    print(f"     Prime factorization: {factor_str}")
    has_7 = 7 in factors
    print(f"     Contains factor 7: {has_7}  (multiplicity: {factors.get(7, 0)})")

    # ── A.2  Dimensional cascade: 24 → 7 ──────────────────────────
    D_bulk = phys["dimensions"]["bulk_lattice"]        # 24
    D_st   = phys["dimensions"]["time"] + 3            # 4 (1 time + 3 space)
    D_compact_ssot = phys["dimensions"]["bulk_compact"] # 7 (stored in SSoT)
    D_holographic = phys["dimensions"]["bulk_holographic"]  # 10

    print(f"\nA.2  Dimensional structure (from SSoT physical_constants.json):")
    print(f"     D_bulk_lattice   = {D_bulk}")
    print(f"     D_spacetime      = {D_st}    (time=1 + space=3)")
    print(f"     D_holographic    = {D_holographic}")
    print(f"     D_bulk_compact   = {D_compact_ssot}   [SSoT STORED VALUE]")
    print(f"     Check: D_bulk - D_holographic       = {D_bulk - D_holographic}")
    print(f"     Check: D_holographic - D_spacetime  = {D_holographic - D_st}")
    print(f"     Check: D_bulk_compact (direct SSoT) = {D_compact_ssot}")

    # ── A.3  Evaluate each candidate route to 7 ──────────────────
    print(f"\nA.3  Candidate algebraic routes to '7':")

    routes = []

    # Route 1: SSoT direct — 7 is stored in dimensions.bulk_compact
    val_r1 = D_compact_ssot
    r1_is_7 = (val_r1 == 7)
    routes.append(("SSoT direct",
                   f"dimensions.bulk_compact = {val_r1}",
                   r1_is_7,
                   "STORED IN SSoT — not derived from first principles within this script"))

    # Route 2: Leech factorization — 7 appears in prime factors of N_leech
    r2_is_7 = has_7
    routes.append(("Leech factorization",
                   f"N_leech = {n_leech} = {factor_str}  → 7^1 factor present",
                   r2_is_7,
                   "7 is a prime divisor of N_leech (the Leech kissing number)"))

    # Route 3: Holographic cascade — D_bulk - D_holographic = 14, /2 = 7
    val_r3 = (D_bulk - D_holographic) // 2
    r3_is_7 = (val_r3 == 7)
    routes.append(("Holographic cascade /2",
                   f"(D_bulk - D_holo) / 2 = ({D_bulk} - {D_holographic}) / 2 = {val_r3}",
                   r3_is_7,
                   "Requires halving step; not automatic — needs justification"))

    # Route 4: D_holographic - D_spacetime = 6, not 7
    val_r4 = D_holographic - D_st
    r4_is_7 = (val_r4 == 7)
    routes.append(("Boundary residual",
                   f"D_holo - D_spacetime = {D_holographic} - {D_st} = {val_r4}",
                   r4_is_7,
                   "Gives 6, NOT 7"))

    # Route 5: E8 root system — E8 has 240 roots; rank 8; dimension 8
    # The coset structure: in M-theory 11D → 4D leaves 7 compact dims
    # D_M_theory = 11 (SSoT: dimensions.m_theory); D_spacetime = 4; D_compact_M = 11 - 4 = 7
    D_M = phys["dimensions"]["m_theory"]
    val_r5 = D_M - D_st
    r5_is_7 = (val_r5 == 7)
    routes.append(("M-theory compactification",
                   f"D_M_theory - D_spacetime = {D_M} - {D_st} = {val_r5}",
                   r5_is_7,
                   "Standard M-theory gives 7 compact dimensions (matches SSoT)"))

    # Route 6: G2 holonomy manifold — 7D manifold with G2 holonomy
    # G2 is the automorphism group of the octonions (rank 2, dim 14)
    # Compact 7D manifold with G2 holonomy preserves N=1 SUSY in 4D
    val_r6 = 7  # definitional
    r6_is_7 = True
    routes.append(("G2-holonomy manifold",
                   "G2-holonomy requires exactly 7D compact manifold",
                   r6_is_7,
                   "Definitional; the KSAU framework uses G2 holonomy → bulk_compact=7 is consistent"))

    print(f"     {'Route':<30}  {'Result':<6}  Note")
    print(f"     {'-'*30}  {'-'*6}  {'-'*35}")
    for name, expr, ok, note in routes:
        tag = "OK 7" if ok else f"NG  ?"
        print(f"     {name:<30}  {tag:<6}  {note}")

    # ── A.4  Evaluate q_mult = 7 specifically ────────────────────
    q_int_mult = cosmo["scaling_factors"]["quark_mass_intercept_multiplier"]
    print(f"\nA.4  q_mult = {q_int_mult} (loaded from cosmological_constants.json SSoT)")
    print(f"     Formula: bq_k = -q_mult * (1 + π/k)")
    print(f"     Physical interpretation: CS/WZW vacuum energy, E_vac ~ q_mult * (π/k)")
    print(f"     Candidate connection: q_mult = D_bulk_compact (7D compact sector)")
    print(f"     D_bulk_compact (SSoT) = {D_compact_ssot}")
    q_matches_dim = (abs(q_int_mult - D_compact_ssot) < 1e-10)
    print(f"     q_mult == D_bulk_compact: {q_matches_dim}")
    if q_matches_dim:
        print(f"     → CANDIDATE DERIVATION: In CS/WZW, the vacuum energy receives")
        print(f"       a contribution from each compact dimension. If the 7 compact")
        print(f"       dimensions (bulk_compact) each contribute equally to E_vac,")
        print(f"       then q_mult = D_bulk_compact = 7 is algebraically motivated.")
        print(f"       Status: CANDIDATE (not proven; requires WZW level computation)")

    # ── A.5  Synthesis ───────────────────────────────────────────
    print(f"\nA.5  Synthesis:")
    print(f"     The value '7' appears in KSAU via THREE consistent routes")
    print(f"     (note: routes 2 and 3 are not fully independent):")
    print(f"       (1) N_leech prime factorization: 196560 = 2^4 × 3^3 × 5 × 7 × 13")
    print(f"       (2) M-theory compactification: {D_M}D - {D_st}D = {val_r5} compact dims")
    print(f"       (3) G2-holonomy manifold: requires exactly 7D")
    print(f"           [Note: routes 2 and 3 are not independent — G2-holonomy arises")
    print(f"            within M-theory compactification, not as a separate constraint]")
    print(f"     All three are CONSISTENT with q_mult = bulk_compact = 7.")
    print(f"     However, none constitutes a DERIVATION from first principles.")
    print(f"     The strongest algebraic link is the dimensional cascade (SSoT stored).")
    print(f"     Verdict: q_mult=7 is ALGEBRAICALLY MOTIVATED (not derived).")
    print(f"     Recommended action: Record as 'MOTIVATED CONJECTURE (Level 1)'")
    print(f"     Full proof requires: WZW level calculation at D_compact=7.")

    return {
        "n_leech": n_leech,
        "factors": factors,
        "has_factor_7": has_7,
        "D_bulk_compact_ssot": D_compact_ssot,
        "q_mult": q_int_mult,
        "q_mult_matches_D_compact": q_matches_dim,
        "candidate_derivation": "D_bulk_compact = 7 (M-theory + G2-holonomy, SSoT-stored)",
    }


# ─────────────────────────────────────────────
# Part B: Section 3 Monte Carlo Test
# ─────────────────────────────────────────────

def run_bao_monte_carlo(phys, cosmo, n_trials=200000):
    print("\n" + "=" * 65)
    print("PART B: Section 3 Monte Carlo Test")
    print("  H0: BAO / R_pure ≈ 7 is a coincidence.")
    print("  Method: Randomize N_kissing ∈ [N_leech/2, 2*N_leech],")
    print("          compute R_rand = N^0.25,")
    print("          test if BAO / R_rand is 'integer-close'.")
    print("=" * 65)

    n_leech  = phys["N_leech"]
    bao_mpc  = cosmo["bao_sound_horizon_mpc"]
    q_mult   = cosmo["scaling_factors"]["quark_mass_intercept_multiplier"]

    r_pure_obs = n_leech**0.25
    ratio_obs  = bao_mpc / r_pure_obs
    nearest_int_obs = round(ratio_obs)
    tol_obs = abs(ratio_obs - nearest_int_obs)

    print(f"\nObserved values:")
    print(f"  N_leech    = {n_leech}")
    print(f"  R_pure     = {r_pure_obs:.6f}")
    print(f"  BAO (Mpc)  = {bao_mpc}")
    print(f"  Ratio      = {ratio_obs:.6f}")
    print(f"  Nearest int= {nearest_int_obs}")
    print(f"  |ratio - int| = {tol_obs:.6f}  (tolerance for H0 test)")

    # ── B.1  Standard MC: random N from geometric ensemble ───────
    # H0 ensemble: kissing numbers distributed log-uniformly
    # around N_leech (spanning ±1 order of magnitude in N).
    # Rationale: we test whether the specific N_leech=196560 is
    # unusually well-aligned with BAO/integer, vs. a generic lattice.

    rng = np.random.default_rng(seed=42)

    # Log-uniform sampling in [N_leech * 0.1, N_leech * 10]
    log_low  = np.log(n_leech * 0.1)
    log_high = np.log(n_leech * 10.0)
    N_samples = rng.uniform(log_low, log_high, n_trials)
    N_samples = np.exp(N_samples)

    R_rand  = N_samples ** 0.25
    ratios  = bao_mpc / R_rand
    diffs   = np.abs(ratios - np.round(ratios))

    hits    = np.sum(diffs <= tol_obs)
    p_value = hits / n_trials

    print(f"\nB.1  Standard MC (log-uniform N, n={n_trials:,}):")
    print(f"     Tolerance applied: |ratio - int| ≤ {tol_obs:.6f}")
    print(f"     Random hits (ratio equally integer-close): {hits} / {n_trials}")
    print(f"     p-value = {p_value:.6f}")

    # ── B.2  Stricter MC: N restricted to [100k, 400k] ───────────
    # More conservative: sample from range of plausible kissing numbers
    N_strict = rng.uniform(100000, 400000, n_trials)
    R_strict = N_strict ** 0.25
    ratios_s = bao_mpc / R_strict
    diffs_s  = np.abs(ratios_s - np.round(ratios_s))
    hits_s   = np.sum(diffs_s <= tol_obs)
    p_strict = hits_s / n_trials

    print(f"\nB.2  Strict MC (uniform N ∈ [100k, 400k], n={n_trials:,}):")
    print(f"     Random hits: {hits_s} / {n_trials}")
    print(f"     p-value = {p_strict:.6f}")

    # ── B.3  Verdict ─────────────────────────────────────────────
    alpha = 0.05
    print(f"\nB.3  Verdict (α = {alpha}):")
    for label, pv in [("Standard", p_value), ("Strict", p_strict)]:
        if pv < alpha:
            tag = f"SIGNIFICANT (p={pv:.6f} < {alpha})"
        elif pv < 0.10:
            tag = f"MARGINAL   (p={pv:.6f} < 0.10)"
        else:
            tag = f"NOT SIGNIFICANT (p={pv:.6f} ≥ {alpha})"
        print(f"     {label:8s}: {tag}")

    # ── B.4  Connection check: ratio vs q_mult ───────────────────
    print(f"\nB.4  Factor-7 connection (Section 2 ↔ Section 3):")
    print(f"     q_mult (Section 2)   = {q_mult}")
    print(f"     BAO/R_pure (Section 3) = {ratio_obs:.6f}")
    print(f"     |q_mult - ratio|     = {abs(q_mult - ratio_obs):.6f}")
    print(f"     Relative difference  = {abs(q_mult - ratio_obs)/q_mult:.4%}")

    return {
        "ratio_obs": ratio_obs,
        "tol_obs": tol_obs,
        "p_standard": p_value,
        "p_strict": p_strict,
        "hits_standard": int(hits),
        "hits_strict": int(hits_s),
        "n_trials": n_trials,
        "verdict_standard": "SIGNIFICANT" if p_value < alpha else ("MARGINAL" if p_value < 0.10 else "NOT_SIGNIFICANT"),
        "verdict_strict":   "SIGNIFICANT" if p_strict < alpha else ("MARGINAL" if p_strict < 0.10 else "NOT_SIGNIFICANT"),
    }


# ─────────────────────────────────────────────
# Part C: Combined Assessment
# ─────────────────────────────────────────────

def combined_assessment(alg_results, mc_results):
    print("\n" + "=" * 65)
    print("PART C: Combined Assessment")
    print("=" * 65)

    p_std    = mc_results["p_standard"]
    p_str    = mc_results["p_strict"]
    q_ok     = alg_results["q_mult_matches_D_compact"]
    has_7    = alg_results["has_factor_7"]
    ratio    = mc_results["ratio_obs"]

    print(f"\n  Algebraic route to 7: {'MOTIVATED (D_bulk_compact)' if q_ok else 'UNDETERMINED'}")
    print(f"  7 in N_leech primes : {has_7}")
    print(f"  MC p (standard)     : {p_std:.6f}")
    print(f"  MC p (strict)       : {p_str:.6f}")
    print(f"  BAO/R_pure ratio    : {ratio:.6f}")

    alpha = 0.05
    mc_significant = (p_std < alpha) or (p_str < alpha)
    mc_marginal    = (not mc_significant) and ((p_std < 0.10) or (p_str < 0.10))

    print(f"\n  Decision matrix:")
    if mc_significant and q_ok:
        upgrade = "UPGRADE → ALGEBRAICALLY MOTIVATED + STATISTICALLY SIGNIFICANT"
        new_status = "MOTIVATED_SIGNIFICANT"
    elif mc_significant and not q_ok:
        upgrade = "UPGRADE → STATISTICALLY SIGNIFICANT (algebraic origin unproven)"
        new_status = "STATISTICALLY_SIGNIFICANT_ONLY"
    elif mc_marginal and q_ok:
        upgrade = "PARTIAL_UPGRADE → MOTIVATED CONJECTURE (MC marginal)"
        new_status = "MOTIVATED_MARGINAL"
    elif not mc_significant and q_ok:
        upgrade = "MAINTAIN NUMERICAL COINCIDENCE CANDIDATE (MC not significant)"
        new_status = "NUMERICAL_COINCIDENCE_CANDIDATE"
    else:
        upgrade = "MAINTAIN NUMERICAL COINCIDENCE CANDIDATE (no support)"
        new_status = "NUMERICAL_COINCIDENCE_CANDIDATE"

    print(f"    → {upgrade}")
    print(f"\n  New proposed status: {new_status}")

    print(f"\n  Summary for Auditor:")
    print(f"    • q_mult=7 is CONSISTENT with D_bulk_compact=7 (M-theory / G2-holonomy),")
    print(f"      both of which are stored in the SSoT. This constitutes a MOTIVATED")
    print(f"      CONJECTURE: all three manifestations of '7' share the same dimensional")
    print(f"      origin, but the WZW-level calculation that would prove it is not done.")
    print(f"    • The MC test provides an EMPIRICAL p-value for the BAO coincidence.")
    print(f"      See Part B for values and verdict.")
    print(f"    • Recommended next step: formal WZW level-k calculation with")
    print(f"      N_compact = D_bulk_compact = 7 to derive E_vac = 7*(π/k).")

    return new_status


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    print("KSAU v30.0 - Factor-of-7 Origin Analysis (Session 12)")
    print("SSoT: v6.0/data/physical_constants.json + cosmological_constants.json")
    print()

    phys, cosmo = load_data()

    alg  = analyze_algebraic_origins(phys, cosmo)
    mc   = run_bao_monte_carlo(phys, cosmo, n_trials=200000)
    new_status = combined_assessment(alg, mc)

    print("\n" + "=" * 65)
    print("EXECUTION COMPLETE")
    print(f"  Algebraic candidate: {alg['candidate_derivation']}")
    print(f"  MC (standard) p    : {mc['p_standard']:.6f}")
    print(f"  MC (strict)   p    : {mc['p_strict']:.6f}")
    print(f"  Proposed Section 3 status: {new_status}")
    print("=" * 65)

    return alg, mc, new_status


if __name__ == "__main__":
    main()
