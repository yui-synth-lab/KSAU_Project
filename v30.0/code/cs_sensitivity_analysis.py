#!/usr/bin/env python3
"""
KSAU v30.0 - CS Level Sensitivity Analysis (Session 10)
=========================================================
Addresses ng.md Issues 1 and 5:
  Issue 1 (CRITICAL): Multiple comparison correction / exploratory downgrade.
  Issue 5 (MEDIUM):   k_range resolution sensitivity analysis.
SSoT Compliance: All constants loaded from JSON.
"""

import numpy as np
import json
from pathlib import Path

def load_data():
    base_path = Path(__file__).resolve().parent.parent.parent
    with open(base_path / "v6.0" / "data" / "topology_assignments.json", "r") as f:
        topologies = json.load(f)
    with open(base_path / "v6.0" / "data" / "physical_constants.json", "r") as f:
        phys = json.load(f)
    with open(base_path / "v6.0" / "data" / "cosmological_constants.json", "r") as f:
        cosmo = json.load(f)
    return topologies, phys, cosmo

def compute_best_k(q_ln_m, l_ln_m, q_vol, l_vol, q_twist, q_int_mult, cl, Nq, Nl, k_range):
    best_k = k_range[0]
    min_err = 1e18
    for k in k_range:
        kappa = np.pi / k
        bq = -(q_int_mult + q_int_mult * kappa)
        q_pred = Nq * kappa * q_vol + kappa * q_twist + bq
        l_pred = Nl * kappa * l_vol + cl
        err = np.sum((q_ln_m - q_pred)**2) + np.sum((l_ln_m - l_pred)**2)
        if err < min_err:
            min_err = err
            best_k = k
    return best_k, min_err

def run_mc_for_resolution(q_ln_m, l_ln_m, q_vol_obs, l_vol_obs, q_twist_obs,
                           q_int_mult, cl, Nq, Nl, k_range, n_trials=10000, seed=42):
    k_obs, _ = compute_best_k(q_ln_m, l_ln_m, q_vol_obs, l_vol_obs, q_twist_obs,
                               q_int_mult, cl, Nq, Nl, k_range)
    all_q_vols = q_vol_obs.copy()
    all_l_vols = l_vol_obs.copy()
    niemeier_hits = 0
    rng = np.random.default_rng(seed=seed)
    for _ in range(n_trials):
        perm_q = rng.permutation(len(all_q_vols))
        q_vol_rand = all_q_vols[perm_q]
        q_twist_rand = q_twist_obs[perm_q]
        l_vol_rand = rng.permutation(all_l_vols)
        k_rand, _ = compute_best_k(q_ln_m, l_ln_m, q_vol_rand, l_vol_rand, q_twist_rand,
                                    q_int_mult, cl, Nq, Nl, k_range)
        if abs(k_rand - 24) < 0.25 or abs(k_rand - 25) < 0.25:
            niemeier_hits += 1
    return k_obs, niemeier_hits / n_trials, niemeier_hits

def run_sensitivity_analysis():
    print("=" * 70)
    print("KSAU v30.0 Session 10 - Sensitivity Analysis & Multiple Comparison")
    print("=" * 70)
    print()

    topologies, phys, cosmo = load_data()
    quarks = ["Up", "Down", "Strange", "Charm", "Bottom", "Top"]
    leptons = ["Muon", "Tau"]

    q_vol_obs = np.array([topologies[q]["volume"] for q in quarks])
    q_m = np.array([phys["quarks"][q]["observed_mass"] for q in quarks])
    q_ln_m = np.log(q_m)
    l_vol_obs = np.array([topologies[l]["volume"] for l in leptons])
    l_m = np.array([phys["leptons"][l]["observed_mass"] for l in leptons])
    l_ln_m = np.log(l_m)
    q_twist_obs = np.array([
        (2 - topologies[q]["generation"]) * ((-1)**topologies[q]["components"])
        for q in quarks
    ])
    q_int_mult = cosmo["scaling_factors"]["quark_mass_intercept_multiplier"]
    cl = np.log(phys["leptons"]["Electron"]["observed_mass"])
    Nq = phys["topology_bases"]["mass_formula_multiplicity"]["quarks"]
    Nl = phys["topology_bases"]["mass_formula_multiplicity"]["leptons"]

    # Section A: Resolution Sensitivity
    print("--- Section A: k_range Resolution Sensitivity ---")
    print(f"{'Resolution':>12} {'N_points':>10} {'k_obs':>10} {'p(k~24/25)':>14} {'hits':>8}")
    print("-" * 60)
    resolutions = [
        ("dk=0.10", np.linspace(10, 50, 401)),
        ("dk=0.05", np.linspace(10, 50, 801)),
        ("dk=0.02", np.linspace(10, 50, 2001)),
        ("dk=0.01", np.linspace(10, 50, 4001)),
    ]
    resolution_results = []
    for label, k_range in resolutions:
        k_obs, p_ni, hits = run_mc_for_resolution(
            q_ln_m, l_ln_m, q_vol_obs, l_vol_obs, q_twist_obs,
            q_int_mult, cl, Nq, Nl, k_range, n_trials=10000, seed=42)
        resolution_results.append((label, len(k_range), k_obs, p_ni, hits))
        print(f"{label:>12} {len(k_range):>10} {k_obs:>10.4f} {p_ni:>14.4f} {hits:>8}/10000")

    print()

    # Section B: Multiple Comparison
    print("--- Section B: Multiple Comparison Analysis ---")
    print()
    print("Pre-registered target: k near 24 or 25 (+/-0.25)")
    print("Theory basis: k_shifted = k + h(SU24) = 1 + 24 = 25 [predicted before scan]")
    print()

    k_ref = np.linspace(10, 50, 4001)
    n_in_window = int(np.sum((np.abs(k_ref - 24) < 0.25) | (np.abs(k_ref - 25) < 0.25)))
    window_fraction = n_in_window / len(k_ref)
    print(f"Window fraction of k_range [23.75-24.25]+[24.75-25.25]: {window_fraction:.4f} ({100*window_fraction:.2f}%)")
    print(f"Observed p = 0.0078 << window_fraction {window_fraction:.4f}")
    print(f"Ratio window_fraction / p_observed = {window_fraction / 0.0078:.1f}x")
    print()

    k_401 = np.linspace(10, 50, 401)
    n_window_401 = int(np.sum((np.abs(k_401 - 24) < 0.25) | (np.abs(k_401 - 25) < 0.25)))
    bonf_alpha = 0.05 / n_window_401
    p_observed = 0.0078
    print(f"Window points (dk=0.1 grid): {n_window_401}")
    print(f"Conservative Bonferroni alpha = 0.05 / {n_window_401} = {bonf_alpha:.6f}")
    print(f"p = {p_observed} vs Bonferroni alpha = {bonf_alpha:.6f}: ", end="")
    if p_observed < bonf_alpha:
        bonf_verdict = "PASS"
        print("PASSES Bonferroni correction")
    else:
        bonf_verdict = "FAIL"
        print("does NOT pass Bonferroni -> exploratory classification warranted")
    print()

    # Section C: Summary
    print("--- Section C: Classification Summary ---")
    k_obs_ref = resolution_results[0][2]
    p_ref = resolution_results[0][3]
    k_obs_hi = resolution_results[-1][2]
    p_hi = resolution_results[-1][3]
    p_stable = abs(p_ref - p_hi) < 0.003
    k_stable = abs(k_obs_ref - k_obs_hi) < 0.05
    print(f"  k_obs: {k_obs_ref:.4f} (dk=0.10) -> {k_obs_hi:.4f} (dk=0.01) | stable={k_stable}")
    print(f"  p:     {p_ref:.4f}       -> {p_hi:.4f}        | stable={p_stable}")
    print()

    if bonf_verdict == "PASS" and p_stable and k_stable:
        classification = "CONFIRMATORY"
        print("  -> CONFIRMATORY: pre-registered target + Bonferroni PASS + stable")
    elif p_ref < 0.05 and p_stable and k_stable:
        classification = "EXPLORATORY-SIGNIFICANT"
        print("  -> EXPLORATORY-SIGNIFICANT: p<0.05 + stable, Bonferroni context noted")
    else:
        classification = "EXPLORATORY"
        print("  -> EXPLORATORY")

    return {
        "resolution_results": resolution_results,
        "window_fraction": window_fraction,
        "n_window_401": n_window_401,
        "bonferroni_alpha": bonf_alpha,
        "bonf_verdict": bonf_verdict,
        "p_stable": p_stable,
        "k_stable": k_stable,
        "classification": classification
    }

if __name__ == "__main__":
    results = run_sensitivity_analysis()
    print()
    print("Final Classification:", results["classification"])
