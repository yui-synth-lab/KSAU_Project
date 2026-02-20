#!/usr/bin/env python3
"""
KSAU v30.0 - CS Level Monte Carlo Test (Session 9 Fix)
=======================================================
Tests the statistical significance of finding k=25 for the fermion mass hierarchy.

REDESIGNED per Audit Issue 3 (Session 7):
- OLD (REJECTED): Generated random mass values and sorted them (contaminated null).
- NEW (CORRECT):  Keeps observed physical masses fixed; randomizes the topology
                  volume assignments. This correctly tests whether the specific
                  pairing of (quark, topology) is required to produce k≈25.

FIXED per Audit Condition A (Session 8 → Session 9):
- OLD (FLAWED):  q_vol_rand and q_twist_rand were shuffled independently via two
                 separate rng.permutation() calls, resulting in a "double
                 randomization" where no coherent (volume, twist) pair was tested.
- NEW (CORRECT): A single permutation index array (perm_q) is generated once, then
                 applied to BOTH q_vol and q_twist arrays consistently.  Twist
                 factors are topological properties of the slot (not the particle),
                 so they must travel with their corresponding volume.

Null Hypothesis H0:
  "Any random assignment of quark (volume, twist) topology slots to quark masses
   would produce a best-fit k as close to an integer (or as close to 24 or 25)
   as the observed physical assignment."

If p < 0.05, we reject H0 and conclude the physical assignment is special.

SSoT Compliance:
- Loads all constants from JSON files.
- Does NOT hardcode any physical values.
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
    """Finds the best-fit k minimizing total squared error."""
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

def run_significance_test():
    print("=== CS Level Significance Test (Session 8 Redesign) ===")
    print("Null Hypothesis: Volume-to-particle assignment is random.")
    print()

    topologies, phys, cosmo = load_data()

    quarks = ["Up", "Down", "Strange", "Charm", "Bottom", "Top"]
    leptons = ["Muon", "Tau"]  # Electron is fixed anchor

    # --- Physical (observed) data ---
    q_vol_obs = np.array([topologies[q]["volume"] for q in quarks])
    q_m = np.array([phys["quarks"][q]["observed_mass"] for q in quarks])
    q_ln_m = np.log(q_m)

    l_vol_obs = np.array([topologies[l]["volume"] for l in leptons])
    l_m = np.array([phys["leptons"][l]["observed_mass"] for l in leptons])
    l_ln_m = np.log(l_m)

    # Twist factors (tied to topology, not mass — fixed under permutation)
    q_twist_obs = np.array([
        (2 - topologies[q]["generation"]) * ((-1)**topologies[q]["components"])
        for q in quarks
    ])

    # --- SSoT constants ---
    q_int_mult = cosmo["scaling_factors"]["quark_mass_intercept_multiplier"]
    cl = np.log(phys["leptons"]["Electron"]["observed_mass"])
    Nq = phys["topology_bases"]["mass_formula_multiplicity"]["quarks"]
    Nl = phys["topology_bases"]["mass_formula_multiplicity"]["leptons"]

    k_range = np.linspace(10, 50, 401)

    # --- Step 1: Compute observed best-fit k ---
    k_obs, err_obs = compute_best_k(
        q_ln_m, l_ln_m, q_vol_obs, l_vol_obs, q_twist_obs,
        q_int_mult, cl, Nq, Nl, k_range
    )
    print(f"Observed physical assignment:")
    print(f"  Best-fit k = {k_obs:.3f}")
    print(f"  Minimum total squared error = {err_obs:.6f}")
    is_near_integer_obs = abs(k_obs - round(k_obs)) < 0.1
    is_niemeier_obs = (abs(k_obs - 24) < 0.25 or abs(k_obs - 25) < 0.25)
    print(f"  Near integer (±0.1): {is_near_integer_obs}")
    print(f"  Near 24 or 25 (±0.25): {is_niemeier_obs}")
    print()

    # --- Step 2: Monte Carlo under H0 (shuffle volume assignments) ---
    n_trials = 10000
    print(f"Running {n_trials} Monte Carlo trials (volume shuffle)...")

    # Pool of all volumes (quark + lepton) to shuffle
    all_q_vols = q_vol_obs.copy()
    all_l_vols = l_vol_obs.copy()

    integer_hits = 0
    niemeier_hits = 0
    err_distribution = []

    rng = np.random.default_rng(seed=42)  # Reproducible seed

    for _ in range(n_trials):
        # Generate a single permutation index for quarks and apply to BOTH
        # volume and twist arrays.  This ensures (volume, twist) pairs remain
        # coherent — twist is a property of the topology slot, so it must move
        # together with its volume when the slot assignment is randomized.
        perm_q = rng.permutation(len(all_q_vols))
        q_vol_rand = all_q_vols[perm_q]
        q_twist_rand = q_twist_obs[perm_q]

        # Lepton volumes are shuffled independently (no twist factor for leptons).
        l_vol_rand = rng.permutation(all_l_vols)

        k_rand, _ = compute_best_k(
            q_ln_m, l_ln_m, q_vol_rand, l_vol_rand, q_twist_rand,
            q_int_mult, cl, Nq, Nl, k_range
        )

        if abs(k_rand - round(k_rand)) < 0.1:
            integer_hits += 1
        if abs(k_rand - 24) < 0.25 or abs(k_rand - 25) < 0.25:
            niemeier_hits += 1

    p_integer = integer_hits / n_trials
    p_niemeier = niemeier_hits / n_trials

    print()
    print("--- Monte Carlo Results ---")
    print(f"P(random shuffle gives integer k ±0.1):    {p_integer:.4f} ({integer_hits}/{n_trials})")
    print(f"P(random shuffle gives k near 24 or 25):   {p_niemeier:.4f} ({niemeier_hits}/{n_trials})")
    print()

    # --- Step 3: Verdict ---
    alpha = 0.05
    print(f"Significance threshold: α = {alpha}")
    if p_niemeier < alpha:
        verdict = "PASSED"
        msg = "Finding k~25 with the physical volume assignment is statistically significant (p < 0.05). H0 rejected."
    elif p_niemeier < 0.10:
        verdict = "MARGINAL"
        msg = f"p={p_niemeier:.4f} is below 0.10 but above 0.05. Evidence is suggestive but not conclusive."
    else:
        verdict = "FAILED — STATISTICALLY REJECTED"
        msg = f"p={p_niemeier:.4f} >= 0.05. Random volume assignments frequently produce k near 24 or 25. H0 cannot be rejected."

    print(f"CONCLUSION: {verdict}")
    print(f"  {msg}")

    return {
        "k_observed": float(k_obs),
        "p_integer": p_integer,
        "p_niemeier": p_niemeier,
        "verdict": verdict,
        "n_trials": n_trials
    }

if __name__ == "__main__":
    results = run_significance_test()
