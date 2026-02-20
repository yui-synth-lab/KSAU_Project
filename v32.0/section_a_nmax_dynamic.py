#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KSAU v32.0 - Task 0: section_a_numerical_patrol.py n_max dynamic version
=========================================================================
Purpose:
  Migrate fixed N_STAR_MAX=20 in v31.0 section_a_numerical_patrol.py
  to per-(p,scale) dynamic n_max = round(scale/R) + margin.
  Re-run and verify main conclusion (Bonferroni p > 0.0024) unchanged.

Changes from v31.0:
  - N_STAR_MAX = 20 (fixed) -> n_max = round(scale_nominal/R) + margin (dynamic)
  - margin = 5 (specified in v32.0 Roadmap)

Inherited technical debt (v31.0):
  ERR_THRESH = err_7 (circular threshold) remains in Step 4.
  Main conclusion relies on Step 5 multi-comparison results.

SSoT: All constants loaded from v6.0/data/*.json
"""

import sys
import json
import math
import random
from pathlib import Path

# -- SSoT loading --
BASE = Path(__file__).resolve().parent.parent
PHYS_PATH  = BASE / "v6.0" / "data" / "physical_constants.json"
COSMO_PATH = BASE / "v6.0" / "data" / "cosmological_constants.json"

with open(PHYS_PATH, "r", encoding="utf-8") as f:
    phys = json.load(f)
with open(COSMO_PATH, "r", encoding="utf-8") as f:
    cosmo = json.load(f)

print("=" * 60)
print("SSoT Load Confirmation [v32.0 n_max dynamic]")
print(f"  Physical constants : {PHYS_PATH}")
print(f"  Cosmological consts: {COSMO_PATH}")
print("=" * 60)

# -- Constants extraction (SSoT) --
N_LEECH      = phys["N_leech"]                    # 196560
R_S          = cosmo["bao_sound_horizon_mpc"]      # 147.09 Mpc
H0           = cosmo["H0_planck"]                  # 67.4 km/s/Mpc
C_LIGHT_KM_S = phys["c_light_km_s"]               # 299792.458 km/s
D_HUBBLE     = C_LIGHT_KM_S / H0                  # ~4448 Mpc
D_CMB        = cosmo["cmb_comoving_distance_mpc"]  # 13818.0 Mpc

print()
print("-- Cosmological Scales (SSoT values) --")
print(f"  N_leech           = {N_LEECH}")
print(f"  r_s (BAO)         = {R_S:.4f} Mpc")
print(f"  H0 (Planck)       = {H0:.2f} km/s/Mpc")
print(f"  d_H = c/H0        = {D_HUBBLE:.2f} Mpc")
print(f"  d_CMB             = {D_CMB:.1f} Mpc")

# -- Step 1: N_leech roots --
EXPONENT_DENOMINATORS = [2, 3, 4, 6, 8, 12, 24]
roots = {}
for p in EXPONENT_DENOMINATORS:
    roots[p] = N_LEECH ** (1.0 / p)

print()
print("-- Step 1: N_leech roots --")
for p, val in roots.items():
    print(f"  N^{{1/{p}}} = {val:.6f}")

cosmo_scales = {
    "r_s (BAO)  ": R_S,
    "d_H (Hubble)": D_HUBBLE,
    "d_CMB      ": D_CMB,
}

scale_nominals = {
    "r_s (BAO)  ": R_S,
    "d_H (Hubble)": D_HUBBLE,
    "d_CMB      ": D_CMB,
}

# -- v32.0 Change: dynamic n_max --
MARGIN = 5

def compute_nmax_dynamic(scale_nominal, R):
    """
    Dynamic n_max per (p, scale): n_max = round(scale_nominal / R) + margin
    """
    n_nominal = round(scale_nominal / R)
    return max(n_nominal + MARGIN, 1)

print()
print(f"-- v32.0 Change: n_max dynamic (margin={MARGIN}) --")
print(f"  n_max = round(scale_nominal / R) + {MARGIN}")
print()
print(f"  {'p':>4}  {'R':>10}  {'rs_nmax':>8}  {'dH_nmax':>8}  {'dCMB_nmax':>10}")
print("  " + "-" * 48)
for p, R in roots.items():
    nmax_rs   = compute_nmax_dynamic(R_S,     R)
    nmax_dh   = compute_nmax_dynamic(D_HUBBLE, R)
    nmax_dcmb = compute_nmax_dynamic(D_CMB,   R)
    print(f"  {p:>4}  {R:>10.4f}  {nmax_rs:>8d}  {nmax_dh:>8d}  {nmax_dcmb:>10d}")

# -- Step 3: N^{1/4}/r_s check --
print()
print("=" * 60)
print("-- Step 3: N^{1/4}/r_s ratio (compare v31.0) --")
R4          = roots[4]
ratio_r4_rs = R_S / R4
err_7       = abs(ratio_r4_rs - 7.0) / 7.0

print(f"  R = N^{{1/4}} = {R4:.6f}")
print(f"  r_s / R      = {ratio_r4_rs:.6f}  (target: ~7)")
print(f"  err |ratio - 7| / 7 = {err_7:.4%}")
print(f"  (Same as v31.0: constants loaded from SSoT)")

# -- Step 4: Monte Carlo test (dynamic n_max) --
N_MC           = 10_000
RS_MIN, RS_MAX = 50.0, 500.0
N_MAX_DYN_RS   = compute_nmax_dynamic(R_S, R4)
ERR_THRESH     = err_7  # NOTE: circular threshold inherited from v31.0

random.seed(42)
hit_count = 0
for _ in range(N_MC):
    rs_rand    = random.uniform(RS_MIN, RS_MAX)
    ratio_rand = rs_rand / R4
    n_rand     = round(ratio_rand)
    if 1 <= n_rand <= N_MAX_DYN_RS:
        err_rand = abs(ratio_rand - n_rand) / n_rand
        if err_rand <= ERR_THRESH:
            hit_count += 1

mc_p = hit_count / N_MC

print()
print("-- Step 4: Monte Carlo test (dynamic n_max) --")
print(f"  H0: r_s ~ Uniform[{RS_MIN},{RS_MAX}] Mpc")
print(f"  err_thresh: {ERR_THRESH:.4%}  [NOTE: circular threshold, v31.0 debt]")
print(f"  n range: [1, {N_MAX_DYN_RS}]  [dynamic: round({R_S:.2f}/{R4:.4f}) + {MARGIN} = {N_MAX_DYN_RS}]")
print(f"  v31.0 fixed: N_STAR_MAX = 20  -> change: {N_MAX_DYN_RS - 20:+d}")
print(f"  N_MC = {N_MC:,}")
print(f"  hits = {hit_count:,}")
print(f"  MC p = {mc_p:.4f}")
if mc_p < 0.05:
    print(f"  -> p < 0.05: significant (H0 rejected)")
else:
    print(f"  -> p = {mc_p:.3f} > 0.05: not significant")

# -- Step 5: Systematic survey (dynamic n_max) --
scale_ranges = {
    "r_s (BAO)  ": (50.0,   500.0),
    "d_H (Hubble)": (3000.0, 6000.0),
    "d_CMB      ": (8000.0, 20000.0),
}

print()
print("=" * 60)
print("-- Step 5: Systematic survey (all roots x all scales, dynamic n_max) --")
print(f"  (N_MC={N_MC}, n_max=dynamic)")
print()
print(f"  {'p':>4}  {'scale':>14}  {'ratio':>7}  {'n*':>4}  {'nmax':>5}  {'err_obs':>8}  {'MC_p':>8}  sig")
print("  " + "-" * 68)

survey_results = []
for p, R in roots.items():
    for scale_name, scale_val in cosmo_scales.items():
        ratio  = scale_val / R
        n_star = max(round(ratio), 1)
        err_obs = abs(ratio - n_star) / n_star

        n_max_dyn = compute_nmax_dynamic(scale_nominals[scale_name], R)

        s_min, s_max = scale_ranges[scale_name]
        hits = 0
        for _ in range(N_MC):
            s_rand = random.uniform(s_min, s_max)
            r_rand = s_rand / R
            n_r    = round(r_rand)
            if 1 <= n_r <= n_max_dyn:
                if abs(r_rand - n_r) / n_r <= err_obs:
                    hits += 1
        p_val = hits / N_MC
        sig   = "* p<0.05" if p_val < 0.05 else ""
        survey_results.append((p, scale_name.strip(), ratio, n_star, err_obs, p_val, n_max_dyn))
        print(f"  {p:>4}  {scale_name:>14}  {ratio:>7.3f}  {n_star:>4d}  {n_max_dyn:>5d}  {err_obs:>8.4%}  {p_val:>8.4f}  {sig}")
    print()

# -- Step 6: Bonferroni correction --
print("=" * 60)
print("-- Step 6: Bonferroni correction --")
n_tests          = len(survey_results)
alpha_corrected  = 0.05 / n_tests
print(f"  n_tests          = {n_tests}")
print(f"  alpha_corrected  = 0.05 / {n_tests} = {alpha_corrected:.6f}")
print()

sig_after_bonf = [r for r in survey_results if r[5] < alpha_corrected]
print(f"  Significant after Bonferroni: {len(sig_after_bonf)}")

p4_rs_rec = next((r for r in survey_results if r[0]==4 and "BAO" in r[1]), None)
if p4_rs_rec:
    _, _, rv, nv, ev, pv, nmv = p4_rs_rec
    print()
    print(f"  N^{{1/4}}/r_s ~ 7 entry:")
    print(f"    ratio    = {rv:.4f}")
    print(f"    n_max    = {nmv}  (v31.0: 20, change: {nmv-20:+d})")
    print(f"    err_obs  = {ev:.4%}")
    print(f"    MC p     = {pv:.4f}")
    print(f"    Bonf threshold = {alpha_corrected:.6f}")
    if pv < alpha_corrected:
        print(f"    -> SIGNIFICANT after Bonferroni (p={pv:.4f} < {alpha_corrected:.6f})")
    else:
        print(f"    -> NOT significant after Bonferroni (p={pv:.4f} > {alpha_corrected:.6f})")
        print(f"    -> Main conclusion: SAME as v31.0 (no significance)")

# -- Step 7: v31.0 comparison --
print()
print("=" * 60)
print("-- Step 7: v31.0 fixed n_max=20 vs v32.0 dynamic comparison --")
print()
print(f"  {'p':>4}  {'scale':>14}  {'v31_nmax':>8}  {'v32_nmax':>8}  diff")
print("  " + "-" * 48)
for rec in survey_results:
    p, sn, ratio, ns, err, pv, nmax_v32 = rec
    diff = nmax_v32 - 20
    print(f"  {p:>4}  {sn:>14}  {20:>8d}  {nmax_v32:>8d}  {diff:+d}")

# -- Final verdict --
print()
print("=" * 60)
print("-- Task 0 Final Verdict --")
print()
print("  Success criteria (v32.0 Roadmap Task 0):")
print("  [x] n_max dynamic implementation: DONE")
print("  [x] Re-run: DONE")

if not sig_after_bonf:
    print(f"  [x] Main conclusion unchanged: ALL {n_tests} combinations NOT significant after Bonferroni")
    print()
    print("  *** Task 0: COMPLETED ***")
    print("    n_max dynamic changes n_max values significantly for large-scale combos,")
    print("    but Bonferroni-corrected main conclusion 'not significant' is UNCHANGED.")
    print("    -> Task 0 SUCCESS CRITERIA: FULLY ACHIEVED")
else:
    print(f"  [!] Main conclusion CHANGED: {len(sig_after_bonf)} combinations significant after Bonferroni")
    print("    -> Requires additional investigation")

print()
print("=" * 60)
print("  Task 0 (n_max dynamic): COMPLETE")
print("=" * 60)
