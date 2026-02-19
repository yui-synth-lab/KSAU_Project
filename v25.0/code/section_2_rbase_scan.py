#!/usr/bin/env python3
"""
KSAU v25.0 Section 2 — R_base Universality Re-evaluation
=========================================================
Physical motivation: v24.0 showed R_base_SSoT = 3/(2κ) = 11.459 Mpc/h
deviates 13.6% from best-fit R_base = 9.896 Mpc/h.
"D=3 (spatial dimensions)" derivation is insufficiently justified.

This section:
2a. Scan D ∈ [1, 24] and find D_opt minimising LOO-CV R_base deviation
2b. R_base as free parameter in the Session 5 LOO-CV framework
2c. Declare final status: SSoT maintained / modified / downgraded

Author: KSAU v25.0 Simulation Kernel — Section 2
Date:   2026-02-19
"""

import sys, json, math
import numpy as np
from pathlib import Path
from scipy.optimize import minimize_scalar, minimize

BASE = Path("E:/Obsidian/KSAU_Project")
sys.path.insert(0, str(BASE / "v23.0" / "code"))
from loo_cv_engine_v23_final_audit import LOOCVFinalAudit

CONFIG_PATH = str(BASE / "v23.0" / "data" / "cosmological_constants.json")
WL5_CONFIG  = str(BASE / "v25.0" / "data" / "wl5_survey_config.json")

KAPPA       = math.pi / 24
BETA_SSoT   = 13.0 / 6.0
R_BASE_SSoT = 3.0 / (2 * KAPPA)   # = 11.459 Mpc/h

# SSoT Leech shell magnitudes (r² = 2n for n=1..8)
LEECH_SHELLS = {
    1: math.sqrt(2),
    2: 2.0,
    3: math.sqrt(6),
    4: 2 * math.sqrt(2),
    5: math.sqrt(10),
    6: 2 * math.sqrt(3),
    7: math.sqrt(14),
    8: 4.0,
}
SSOT_QUINTUPLE   = (7, 6, 5, 3, 1)   # DES, CFHTLenS, DLS, HSC, KiDS (k_eff ascending)
BESTFIT_QUINTUPLE = (8, 5, 4, 3, 2)   # v24.0 best-fit (Session 6/7)

# Session 5 LOO-CV R₀ canonical values
R0_LOO_S5 = {
    "DES Y3":      39.6295,
    "CFHTLenS":    29.5562,
    "DLS":         26.2132,
    "HSC Y3":      27.2116,
    "KiDS-Legacy": 19.6971,
}
SURVEY_ORDER = ["DES Y3", "CFHTLenS", "DLS", "HSC Y3", "KiDS-Legacy"]


def load_surveys():
    with open(WL5_CONFIG, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    return cfg["surveys"]


# ─── Section 2a: D-scan───────────────────────────────────────────────────────
def d_scan_analysis():
    """
    2a: Scan D ∈ [1, 24] to find D_opt such that R_base(D) = D/(2κ)
    minimises the CV of (R₀_loo_i / shell_mag_i) for a given quintuple.

    Physical meaning: we're asking "which D gives the most consistent
    R_base across all 5 surveys?"

    Note: the best-fit R_base that minimises CV is independent of D
    (it's just mean(R₀_loo_i / shell_i)). What varies with the quintuple
    choice is the CV. This section scans D to compare R_base(D) with
    the empirical best-fit mean R_base.
    """
    r0_arr = np.array([R0_LOO_S5[n] for n in SURVEY_ORDER])

    # Compute implied R_base for each survey under SSoT quintuple
    r_bases_ssot = np.array([R0_LOO_S5[n] / LEECH_SHELLS[SSOT_QUINTUPLE[i]]
                              for i, n in enumerate(SURVEY_ORDER)])
    r_base_mean_ssot = float(r_bases_ssot.mean())
    r_base_std_ssot  = float(r_bases_ssot.std())
    cv_ssot = r_base_std_ssot / r_base_mean_ssot

    # Compute implied R_base for each survey under best-fit quintuple
    r_bases_bf = np.array([R0_LOO_S5[n] / LEECH_SHELLS[BESTFIT_QUINTUPLE[i]]
                            for i, n in enumerate(SURVEY_ORDER)])
    r_base_mean_bf = float(r_bases_bf.mean())
    cv_bf = float(r_bases_bf.std() / r_bases_bf.mean())

    # D_opt = 2κ × R_base_mean (minimum-CV R_base under each quintuple)
    D_opt_ssot  = 2 * KAPPA * r_base_mean_ssot
    D_opt_bf    = 2 * KAPPA * r_base_mean_bf
    D_ssot_ref  = 3.0  # SSoT uses D=3

    # Scan D ∈ [0.5, 10] continuously (not just integers)
    D_scan = np.linspace(0.5, 10.0, 1000)
    R_base_scan = D_scan / (2 * KAPPA)

    # For each D, compute deviation of R_base(D) from the empirical R_base_mean
    # under SSoT quintuple
    dev_ssot = np.abs(R_base_scan - r_base_mean_ssot) / r_base_mean_ssot * 100.0
    dev_bf   = np.abs(R_base_scan - r_base_mean_bf)   / r_base_mean_bf   * 100.0

    # Integer D candidates
    integer_candidates = []
    for D_int in range(1, 25):
        R_int = D_int / (2 * KAPPA)
        dev_from_ssot_empi = abs(R_int - r_base_mean_ssot) / r_base_mean_ssot * 100.0
        dev_from_bf_empi   = abs(R_int - r_base_mean_bf)   / r_base_mean_bf   * 100.0
        integer_candidates.append({
            "D":       D_int,
            "R_base":  round(R_int, 4),
            "dev_from_ssot_empirical_pct": round(dev_from_ssot_empi, 2),
            "dev_from_bf_empirical_pct":   round(dev_from_bf_empi, 2),
        })

    # Per-survey implied R_base and D for both quintuples
    per_survey_ssot = []
    per_survey_bf   = []
    for i, name in enumerate(SURVEY_ORDER):
        R_b_s = R0_LOO_S5[name] / LEECH_SHELLS[SSOT_QUINTUPLE[i]]
        R_b_b = R0_LOO_S5[name] / LEECH_SHELLS[BESTFIT_QUINTUPLE[i]]
        D_s   = 2 * KAPPA * R_b_s
        D_b   = 2 * KAPPA * R_b_b
        per_survey_ssot.append({
            "survey": name,
            "shell": SSOT_QUINTUPLE[i],
            "R_base_implied": round(R_b_s, 4),
            "D_implied": round(D_s, 4),
        })
        per_survey_bf.append({
            "survey": name,
            "shell": BESTFIT_QUINTUPLE[i],
            "R_base_implied": round(R_b_b, 4),
            "D_implied": round(D_b, 4),
        })

    return {
        "ssot_quintuple": {
            "quintuple":       list(SSOT_QUINTUPLE),
            "r_base_mean":     round(r_base_mean_ssot, 4),
            "r_base_std":      round(r_base_std_ssot, 4),
            "cv_pct":          round(cv_ssot * 100, 4),
            "D_opt":           round(D_opt_ssot, 4),
            "per_survey":      per_survey_ssot,
        },
        "bestfit_quintuple": {
            "quintuple":       list(BESTFIT_QUINTUPLE),
            "r_base_mean":     round(r_base_mean_bf, 4),
            "cv_pct":          round(cv_bf * 100, 4),
            "D_opt":           round(D_opt_bf, 4),
            "per_survey":      per_survey_bf,
        },
        "D_ssot_reference":   D_ssot_ref,
        "R_base_SSoT_formula": round(R_BASE_SSoT, 4),
        "integer_D_candidates": integer_candidates[:12],  # D=1..12
        "D_opt_ssot_quintuple": round(D_opt_ssot, 4),
        "D_opt_bf_quintuple":   round(D_opt_bf, 4),
        "dev_ssot_D3_from_opt_pct": round(
            abs(D_ssot_ref - D_opt_ssot) / D_opt_ssot * 100, 2),
        "nearest_integer_to_Dopt_ssot": int(round(D_opt_ssot)),
        "nearest_integer_to_Dopt_bf":   int(round(D_opt_bf)),
        "physical_notes": {
            "D=3_justification": "SSoT uses D=3 (spatial dimensions). R_base = 3/(2κ).",
            "D_opt_ssot":  (f"D_opt (SSoT quintuple) = {D_opt_ssot:.4f} ≈ "
                            f"{round(D_opt_ssot, 2)}. "
                            f"Not equal to D=3. Nearest integer = {int(round(D_opt_ssot))}."),
            "D_opt_bf":    (f"D_opt (best-fit quintuple) = {D_opt_bf:.4f} ≈ "
                            f"{round(D_opt_bf, 2)}. "
                            f"Not equal to D=3. Nearest integer = {int(round(D_opt_bf))}."),
        },
    }


# ─── Section 2b: R_base as free parameter in LOO-CV ──────────────────────────
def rbase_free_loo_cv(surveys):
    """
    2b: Add R_base as a free parameter to the LOO-CV.
    For each fold, optimise (R_base, β) to minimise S₈ chi².
    Compare with SSoT-fixed R_base.

    WARNING: With the Leech model, R₀ = R_base × shell_mag.
    This becomes: 2 free params (R_base, β) for 4 training surveys.
    Not over-complete.
    """
    engine = LOOCVFinalAudit(config_path=CONFIG_PATH)
    survey_list = list(surveys.keys())

    def loo_cv_cost(params, training_surveys):
        R_base, beta = params
        if R_base <= 0 or beta <= 0:
            return 1e9
        chi2 = 0.0
        for i, name in enumerate(training_surveys):
            sv     = surveys[name]
            shell_idx = SSOT_QUINTUPLE[survey_list.index(name)]
            r0_pred   = R_base * LEECH_SHELLS[shell_idx]
            z = sv["z_eff"]
            a = 1.0 / (1.0 + z)
            s8_pred_z = engine.predict_s8_z(z, r0_pred, beta, True)
            s8_obs_z  = sv["S8_obs"] * (a ** 0.55)
            s8_err_z  = sv["S8_err"] * (a ** 0.55)
            chi2 += ((s8_pred_z - s8_obs_z) / s8_err_z) ** 2
        return chi2

    results = {}
    for held_out in survey_list:
        train = [n for n in survey_list if n != held_out]
        res = minimize(loo_cv_cost, [10.0, BETA_SSoT], args=(train,),
                       method="Nelder-Mead",
                       options={"xatol": 1e-5, "fatol": 1e-5, "maxiter": 3000})
        R_base_opt, beta_opt = res.x

        sv      = surveys[held_out]
        idx     = survey_list.index(held_out)
        shell   = SSOT_QUINTUPLE[idx]
        r0_pred = R_base_opt * LEECH_SHELLS[shell]
        z_ho    = sv["z_eff"]
        a_ho    = 1.0 / (1.0 + z_ho)
        s8_pred = engine.predict_s8_z(z_ho, r0_pred, beta_opt, True)
        s8_obs_z  = sv["S8_obs"] * (a_ho ** 0.55)
        s8_err_z  = sv["S8_err"] * (a_ho ** 0.55)
        tension   = (s8_pred - s8_obs_z) / s8_err_z

        results[held_out] = {
            "R_base_loo":    round(R_base_opt, 4),
            "beta_loo":      round(beta_opt, 4),
            "D_loo":         round(2 * KAPPA * R_base_opt, 4),
            "r0_pred":       round(r0_pred, 3),
            "s8_pred":       round(s8_pred, 4),
            "s8_obs_z":      round(s8_obs_z, 4),
            "tension":       round(tension, 4),
        }

    tensions = [v["tension"] for v in results.values()]
    mae = float(np.mean(np.abs(tensions)))

    return {
        "per_fold": results,
        "mae_all":  round(mae, 4),
        "n_params": 2,
        "note":     "2 free params (R_base, β) per fold / 4 training data points",
    }


# ─── Section 2c: Final R_base status declaration ──────────────────────────────
def declare_rbase_status(d_scan, rbase_loo):
    """
    2c: Based on D-scan and LOO-CV results, declare R_base status.
    """
    D_opt_bf   = d_scan["D_opt_bf_quintuple"]
    R_base_bf  = D_opt_bf / (2 * KAPPA)
    dev_from_ssot_pct = abs(R_BASE_SSoT - R_base_bf) / R_BASE_SSoT * 100.0

    # Is D_opt an integer or known constant?
    nearest_int = round(D_opt_bf)
    delta_to_nearest_int = abs(D_opt_bf - nearest_int) / D_opt_bf * 100.0

    # Is D_opt close to e, π-1, sqrt(7), etc?
    special = {
        "e":          (math.e, abs(D_opt_bf - math.e) / D_opt_bf * 100),
        "pi-1":       (math.pi - 1, abs(D_opt_bf - (math.pi - 1)) / D_opt_bf * 100),
        "sqrt(7)":    (math.sqrt(7), abs(D_opt_bf - math.sqrt(7)) / D_opt_bf * 100),
        "5/2":        (2.5, abs(D_opt_bf - 2.5) / D_opt_bf * 100),
        "8*kappa":    (8 * KAPPA, abs(D_opt_bf - 8 * KAPPA) / D_opt_bf * 100),
        "pi*kappa":   (math.pi * KAPPA, abs(D_opt_bf - math.pi * KAPPA) / D_opt_bf * 100),
    }
    closest_special = min(special.items(), key=lambda x: x[1][1])

    if dev_from_ssot_pct > 10.0 and delta_to_nearest_int > 5.0:
        status = "DOWNGRADED"
        verdict = (
            f"R_base_SSoT = 3/(2κ) = {R_BASE_SSoT:.4f} Mpc/h deviates {dev_from_ssot_pct:.1f}% "
            f"from best-fit R_base = {R_base_bf:.4f} Mpc/h (D_opt = {D_opt_bf:.4f}). "
            f"D_opt is not an integer (nearest={nearest_int}, Δ={delta_to_nearest_int:.1f}%). "
            f"D=3 (spatial dimension) is not supported by LOO-CV data. "
            f"STATUS: R_base DOWNGRADED to 'approximate heuristic'."
        )
        new_ssot = f"R_base_best_fit = {R_base_bf:.4f} Mpc/h (empirical, no first-principles derivation)"
    elif dev_from_ssot_pct < 5.0:
        status = "MAINTAINED"
        verdict = (
            f"R_base_SSoT = {R_BASE_SSoT:.4f} Mpc/h deviates only {dev_from_ssot_pct:.1f}% "
            f"from best-fit — within acceptable tolerance. STATUS: SSoT MAINTAINED."
        )
        new_ssot = f"R_base_SSoT = {R_BASE_SSoT:.4f} Mpc/h (maintained)"
    else:
        status = "MODIFIED"
        verdict = (
            f"R_base_SSoT deviates {dev_from_ssot_pct:.1f}%. "
            f"D_opt = {D_opt_bf:.4f} is closest to nearest integer D={nearest_int} "
            f"by {delta_to_nearest_int:.1f}%. Requires further theoretical investigation. "
            f"STATUS: MODIFIED — propose R_base = D_opt/(2κ) = {R_base_bf:.4f} Mpc/h."
        )
        new_ssot = f"R_base_modified = D_opt/(2κ) = {R_base_bf:.4f} Mpc/h (provisional)"

    return {
        "status":                  status,
        "R_base_ssot":             round(R_BASE_SSoT, 4),
        "R_base_best_fit":         round(R_base_bf, 4),
        "D_opt":                   round(D_opt_bf, 4),
        "deviation_from_ssot_pct": round(dev_from_ssot_pct, 2),
        "nearest_integer_D":       nearest_int,
        "delta_to_nearest_int_pct": round(delta_to_nearest_int, 2),
        "closest_special_constant": {
            "name":       closest_special[0],
            "value":      round(closest_special[1][0], 6),
            "deviation_pct": round(closest_special[1][1], 2),
        },
        "verdict":                 verdict,
        "new_ssot_recommendation": new_ssot,
        "all_special_deviations":  {k: {"value": round(v[0], 6), "dev_pct": round(v[1], 2)}
                                     for k, v in special.items()},
    }


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 76)
    print("KSAU v25.0 Section 2 — R_base Universality Re-evaluation")
    print(f"SSoT: R_base = 3/(2κ) = {R_BASE_SSoT:.4f} Mpc/h (D=3)")
    print("=" * 76)

    surveys = load_surveys()

    # 2a: D-scan
    print("\nSection 2a: D-scan analysis...")
    d_scan = d_scan_analysis()
    print(f"  SSoT quintuple: D_opt = {d_scan['D_opt_ssot_quintuple']:.4f}, "
          f"R_base_empirical = {d_scan['ssot_quintuple']['r_base_mean']:.4f} Mpc/h, "
          f"CV = {d_scan['ssot_quintuple']['cv_pct']:.2f}%")
    print(f"  Best-fit quintuple: D_opt = {d_scan['D_opt_bf_quintuple']:.4f}, "
          f"R_base_empirical = {d_scan['bestfit_quintuple']['r_base_mean']:.4f} Mpc/h, "
          f"CV = {d_scan['bestfit_quintuple']['cv_pct']:.2f}%")
    print(f"  SSoT D=3: R_base = {R_BASE_SSoT:.4f} Mpc/h")
    print(f"  Deviation of D=3 from D_opt_SSoT: "
          f"{d_scan['dev_ssot_D3_from_opt_pct']:.2f}%")

    print("\n  Integer D candidates (D=1..8):")
    for ic in d_scan["integer_D_candidates"][:8]:
        print(f"    D={ic['D']:2d} → R_base={ic['R_base']:.4f} Mpc/h | "
              f"dev_ssot_empi={ic['dev_from_ssot_empirical_pct']:.1f}% | "
              f"dev_bf_empi={ic['dev_from_bf_empirical_pct']:.1f}%")

    # 2b: R_base free LOO-CV
    print("\nSection 2b: R_base + β free LOO-CV (SSoT quintuple)...")
    rbase_loo = rbase_free_loo_cv(surveys)
    print(f"  LOO-CV MAE (R_base free) = {rbase_loo['mae_all']:.4f}σ")
    print(f"  Per-fold R_base values:")
    for name, fold in rbase_loo["per_fold"].items():
        print(f"    {name:<14} R_base={fold['R_base_loo']:.4f} Mpc/h, "
              f"D={fold['D_loo']:.4f}, β={fold['beta_loo']:.4f}, "
              f"tension={fold['tension']:+.4f}σ")

    # 2c: Status declaration
    print("\nSection 2c: R_base status declaration...")
    status_decl = declare_rbase_status(d_scan, rbase_loo)
    print(f"\n  STATUS: {status_decl['status']}")
    print(f"  {status_decl['verdict']}")
    print(f"\n  Closest special constant to D_opt: "
          f"{status_decl['closest_special_constant']['name']} = "
          f"{status_decl['closest_special_constant']['value']:.4f} "
          f"(dev={status_decl['closest_special_constant']['deviation_pct']:.2f}%)")

    # Save results
    results = {
        "date":    "2026-02-19",
        "section": "Section 2",
        "ssot": {"kappa": KAPPA, "beta_ssot": BETA_SSoT, "R_base_SSoT": R_BASE_SSoT},
        "section_2a_d_scan":   d_scan,
        "section_2b_rbase_loo": rbase_loo,
        "section_2c_status":   status_decl,
    }

    out_path = BASE / "v25.0" / "data" / "section_2_results.json"
    with open(str(out_path), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved → {out_path}")
    return results


if __name__ == "__main__":
    main()
