#!/usr/bin/env python3
"""
KSAU v34.0 - Section A: Leave-One-Out Cross-Validation (Internal Robustness Check)
====================================================================================
Purpose:
  Test whether the Section 2 result (best-fit k near 24/25, p=0.0078) is robust
  to removal of individual particles. This is NOT a truly independent reproduction
  (the dataset is the same), but it tests if the result is driven by a single
  influential particle.

Design:
  - For each of 8 fermions (6 quarks + 2 leptons), remove one particle and run
    the same MC permutation test on the remaining 7.
  - If the result holds for all LOO subsets, it is more robust than if it
    depends on a single particle.

Null Hypothesis (same as v30.0 Section 2):
  "Any random assignment of (volume, twist) topology slots to masses would
   produce a best-fit k as close to 24 or 25 as the physical assignment."

SSoT Compliance:
  All constants loaded from JSON files (v6.0/data/).
"""

import numpy as np
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
TOPO_PATH = BASE / "v6.0" / "data" / "topology_assignments.json"
PHYS_PATH = BASE / "v6.0" / "data" / "physical_constants.json"
COSMO_PATH = BASE / "v6.0" / "data" / "cosmological_constants.json"

with open(TOPO_PATH, "r", encoding="utf-8") as f:
    topologies = json.load(f)
with open(PHYS_PATH, "r", encoding="utf-8") as f:
    phys = json.load(f)
with open(COSMO_PATH, "r", encoding="utf-8") as f:
    cosmo = json.load(f)

# SSoT constants
q_int_mult = cosmo["scaling_factors"]["quark_mass_intercept_multiplier"]
cl = np.log(phys["leptons"]["Electron"]["observed_mass"])
Nq = phys["topology_bases"]["mass_formula_multiplicity"]["quarks"]
Nl = phys["topology_bases"]["mass_formula_multiplicity"]["leptons"]

ALL_QUARKS = ["Up", "Down", "Strange", "Charm", "Bottom", "Top"]
ALL_LEPTONS = ["Muon", "Tau"]

K_RANGE = np.linspace(10, 50, 401)
N_TRIALS = 10000
SEED = 42


def get_particle_data(quarks, leptons):
    q_vol = np.array([topologies[q]["volume"] for q in quarks])
    q_m   = np.array([phys["quarks"][q]["observed_mass"] for q in quarks])
    q_ln_m = np.log(q_m)
    q_twist = np.array([
        (2 - topologies[q]["generation"]) * ((-1) ** topologies[q]["components"])
        for q in quarks
    ])
    l_vol = np.array([topologies[l]["volume"] for l in leptons])
    l_m   = np.array([phys["leptons"][l]["observed_mass"] for l in leptons])
    l_ln_m = np.log(l_m)
    return q_vol, q_ln_m, q_twist, l_vol, l_ln_m


def compute_best_k(q_ln_m, l_ln_m, q_vol, l_vol, q_twist, k_range):
    best_k = k_range[0]
    min_err = 1e18
    for k in k_range:
        kappa = np.pi / k
        bq = -(q_int_mult + q_int_mult * kappa)
        q_pred = Nq * kappa * q_vol + kappa * q_twist + bq
        l_pred = Nl * kappa * l_vol + cl
        err = np.sum((q_ln_m - q_pred) ** 2) + np.sum((l_ln_m - l_pred) ** 2)
        if err < min_err:
            min_err = err
            best_k = k
    return best_k, min_err


def run_mc_test(q_vol_obs, q_ln_m, q_twist_obs, l_vol_obs, l_ln_m):
    k_obs, _ = compute_best_k(q_ln_m, l_ln_m, q_vol_obs, l_vol_obs, q_twist_obs, K_RANGE)
    rng = np.random.default_rng(seed=SEED)
    niemeier_hits = 0
    for _ in range(N_TRIALS):
        perm_q = rng.permutation(len(q_vol_obs))
        q_vol_rand   = q_vol_obs[perm_q]
        q_twist_rand = q_twist_obs[perm_q]
        l_vol_rand   = rng.permutation(l_vol_obs)
        k_rand, _ = compute_best_k(q_ln_m, l_ln_m, q_vol_rand, l_vol_rand, q_twist_rand, K_RANGE)
        if abs(k_rand - 24) < 0.25 or abs(k_rand - 25) < 0.25:
            niemeier_hits += 1
    p = niemeier_hits / N_TRIALS
    return k_obs, p, niemeier_hits


def main():
    print("=" * 72)
    print("KSAU v34.0 Section A — Leave-One-Out Cross-Validation")
    print("Internal robustness check (NOT truly independent reproduction)")
    print("=" * 72)
    print()

    # Full dataset (reference)
    q_vol, q_ln_m, q_twist, l_vol, l_ln_m = get_particle_data(ALL_QUARKS, ALL_LEPTONS)
    k_full, p_full, hits_full = run_mc_test(q_vol, q_ln_m, q_twist, l_vol, l_ln_m)
    print(f"[FULL] 6Q+2L: k_obs={k_full:.3f}, p={p_full:.4f} ({hits_full}/{N_TRIALS})")
    print()

    # LOO results
    print(f"{'Removed':>12} {'Nq':>3} {'Nl':>3} {'k_obs':>8} {'p(k~24/25)':>12} {'hits':>8} {'p<0.05':>8}")
    print("-" * 72)
    loo_results = []
    bonf_alpha = 0.05 / 10  # Same conservative Bonferroni as v30.0 (n=10)

    # LOO: remove each quark
    for leave_out in ALL_QUARKS:
        remaining_quarks = [q for q in ALL_QUARKS if q != leave_out]
        if len(remaining_quarks) < 2:
            continue
        q_vol_loo, q_ln_m_loo, q_twist_loo, l_vol_loo, l_ln_m_loo = get_particle_data(
            remaining_quarks, ALL_LEPTONS)
        k_loo, p_loo, hits_loo = run_mc_test(q_vol_loo, q_ln_m_loo, q_twist_loo,
                                              l_vol_loo, l_ln_m_loo)
        sig = "YES" if p_loo < 0.05 else "no"
        print(f"{leave_out:>12} {len(remaining_quarks):>3} {len(ALL_LEPTONS):>3} "
              f"{k_loo:>8.3f} {p_loo:>12.4f} {hits_loo:>8}/{N_TRIALS} {sig:>8}")
        loo_results.append((leave_out, "quark", len(remaining_quarks), len(ALL_LEPTONS),
                            k_loo, p_loo, hits_loo))

    # LOO: remove each lepton
    for leave_out in ALL_LEPTONS:
        remaining_leptons = [l for l in ALL_LEPTONS if l != leave_out]
        if len(remaining_leptons) < 1:
            continue
        q_vol_loo, q_ln_m_loo, q_twist_loo, l_vol_loo, l_ln_m_loo = get_particle_data(
            ALL_QUARKS, remaining_leptons)
        k_loo, p_loo, hits_loo = run_mc_test(q_vol_loo, q_ln_m_loo, q_twist_loo,
                                              l_vol_loo, l_ln_m_loo)
        sig = "YES" if p_loo < 0.05 else "no"
        print(f"{leave_out:>12} {len(ALL_QUARKS):>3} {len(remaining_leptons):>3} "
              f"{k_loo:>8.3f} {p_loo:>12.4f} {hits_loo:>8}/{N_TRIALS} {sig:>8}")
        loo_results.append((leave_out, "lepton", len(ALL_QUARKS), len(remaining_leptons),
                            k_loo, p_loo, hits_loo))

    print()

    # Summary
    p_values = [r[5] for r in loo_results]
    n_sig05 = sum(1 for p in p_values if p < 0.05)
    n_sig_bonf = sum(1 for p in p_values if p < bonf_alpha)
    print(f"Summary:")
    print(f"  LOO subsets: {len(loo_results)}")
    print(f"  p < 0.05:  {n_sig05}/{len(loo_results)}")
    print(f"  p < {bonf_alpha:.4f} (Bonferroni conservative): {n_sig_bonf}/{len(loo_results)}")
    print()

    if n_sig05 == len(loo_results):
        robustness = "ROBUST: All LOO subsets remain p<0.05"
    elif n_sig05 > len(loo_results) // 2:
        robustness = f"MOSTLY ROBUST: {n_sig05}/{len(loo_results)} LOO subsets p<0.05"
    else:
        robustness = f"NOT ROBUST: only {n_sig05}/{len(loo_results)} LOO subsets p<0.05"

    print(f"LOO Robustness: {robustness}")
    print()
    print("NOTE: This is internal LOO-CV, NOT a truly independent reproduction.")
    print("      Independent dataset for truly independent reproduction: NOT AVAILABLE.")
    print("      (Topology volumes are KSAU-internal; no external source exists.)")


if __name__ == "__main__":
    main()
