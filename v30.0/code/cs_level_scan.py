#!/usr/bin/env python3
"""
KSAU v30.0 - Chern-Simons Level Scan (Session 8 Update)
=========================================================
Scans for the optimal 'k' level that minimizes the error in the
fermion mass hierarchy, assuming the S-duality form:
    ln(m) = N * (pi/k) * V + C

Session 8 changes:
- Added R^2 computation per k-level (Issue 6 fix).
- Documented physical derivation of bq_k intercept (Issue 5 fix).

SSoT Compliance:
- Loads kappa and intercepts from JSON.
- Loads multiplicity factors N from JSON.

--- Derivation of the intercept bq_k (Issue 5 documentation) ---
The quark mass intercept bq_k arises from the boundary condition of the
Chern-Simons partition function projected onto the 4D spacetime sector.

In the CS/WZW correspondence, the partition function Z_k contains a
"vacuum energy" term proportional to h/(k+h), where h is the dual Coxeter
number. In the KSAU approximation (large k), this becomes:

    E_vac ~ q_int_mult * (pi/k)

where q_int_mult = 7 (loaded from SSoT: cosmological_constants.json,
scaling_factors.quark_mass_intercept_multiplier).

The physical intercept is therefore:

    bq_k = -E_ground - E_vac
         = -q_int_mult * (1 + pi/k)
         = -(q_int_mult + q_int_mult * kappa_k)

The k-dependence of bq_k reflects the finite-level correction to the
ground state energy; in the k -> infinity (classical) limit, bq_k -> -7.

NOTE: This derivation is a CANDIDATE interpretation. The coefficient 7
(= q_int_mult) is sourced from SSoT but its first-principles algebraic
origin in the KSAU framework has not yet been proven. See Section 3 status.
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

def compute_r2(y_obs, y_pred):
    """Compute R^2 (coefficient of determination)."""
    ss_res = np.sum((y_obs - y_pred)**2)
    ss_tot = np.sum((y_obs - np.mean(y_obs))**2)
    if ss_tot == 0:
        return float('nan')
    return 1.0 - ss_res / ss_tot

def scan_k():
    topologies, phys, cosmo = load_data()

    quarks = ["Up", "Down", "Strange", "Charm", "Bottom", "Top"]
    leptons = ["Muon", "Tau"]

    q_vol = np.array([topologies[q]["volume"] for q in quarks])
    q_m = np.array([phys["quarks"][q]["observed_mass"] for q in quarks])
    q_ln_m = np.log(q_m)

    l_vol = np.array([topologies[l]["volume"] for l in leptons])
    l_m = np.array([phys["leptons"][l]["observed_mass"] for l in leptons])
    l_ln_m = np.log(l_m)

    # Intercepts from SSoT
    # q_int_mult = 7.0; source: cosmological_constants.json -> scaling_factors -> quark_mass_intercept_multiplier
    q_int_mult = cosmo["scaling_factors"]["quark_mass_intercept_multiplier"]

    # Lepton anchor intercept = ln(m_electron)
    cl = np.log(phys["leptons"]["Electron"]["observed_mass"])

    # Multiplicity factors N from SSoT
    Nq = phys["topology_bases"]["mass_formula_multiplicity"]["quarks"]
    Nl = phys["topology_bases"]["mass_formula_multiplicity"]["leptons"]

    # Twist factors (topology-dependent, k-independent)
    q_twist = np.array([
        (2 - topologies[q]["generation"]) * ((-1)**topologies[q]["components"])
        for q in quarks
    ])

    k_range = np.linspace(20, 30, 101)
    results = []

    print(f"{'k':>8}  {'TotalErr':>12}  {'R2_quark':>10}  {'R2_lepton':>10}  {'R2_combined':>12}")
    print("-" * 60)

    for k in k_range:
        kappa_k = np.pi / k

        # Intercept: bq_k = -(q_int_mult * (1 + pi/k))
        # Physical derivation: see module docstring above.
        bq_k = -(q_int_mult + q_int_mult * kappa_k)

        q_pred = Nq * kappa_k * q_vol + kappa_k * q_twist + bq_k
        l_pred = Nl * kappa_k * l_vol + cl

        q_err = np.sum((q_ln_m - q_pred)**2)
        l_err = np.sum((l_ln_m - l_pred)**2)
        total_err = q_err + l_err

        r2_q = compute_r2(q_ln_m, q_pred)
        r2_l = compute_r2(l_ln_m, l_pred)
        # Combined R^2 over all fermions
        all_obs = np.concatenate([q_ln_m, l_ln_m])
        all_pred = np.concatenate([q_pred, l_pred])
        r2_comb = compute_r2(all_obs, all_pred)

        results.append((k, total_err, r2_q, r2_l, r2_comb))

    results_sorted = sorted(results, key=lambda x: x[1])
    best = results_sorted[0]

    # Print top 5 results
    for row in results_sorted[:5]:
        k_v, err, r2q, r2l, r2c = row
        print(f"{k_v:>8.3f}  {err:>12.6f}  {r2q:>10.4f}  {r2l:>10.4f}  {r2c:>12.4f}")

    print()
    print(f"Best-fit k:                {best[0]:.3f}")
    print(f"Minimum total squared error: {best[1]:.6f}")
    print(f"R^2 (quarks only):          {best[2]:.4f}")
    print(f"R^2 (leptons only):         {best[3]:.4f}")
    print(f"R^2 (combined, 8 fermions): {best[4]:.4f}")

    return best

if __name__ == "__main__":
    scan_k()

