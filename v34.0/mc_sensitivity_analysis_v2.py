#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KSAU v34.0 - MC Sensitivity Analysis v2 (Section B-1 fix)
===========================================================
Purpose:
  Fix the n_max issue identified in v33.0 go.md WARNING #1:
  The original script used N_MAX_RS computed from r_s (standard range center)
  for ALL three sampling ranges, causing the wide [30,1000] range to have
  an effectively narrowed null hypothesis space.

Fix:
  Compute n_max dynamically for each range based on the midpoint of that range:
    n_max(range) = compute_nmax(scale_nominal = (rs_min + rs_max) / 2, R4, MARGIN)

SSoT: All constants loaded from v6.0/data/*.json
"""

import json
import random
import sys
from pathlib import Path

BASE       = Path(__file__).resolve().parent.parent
PHYS_PATH  = BASE / "v6.0" / "data" / "physical_constants.json"
COSMO_PATH = BASE / "v6.0" / "data" / "cosmological_constants.json"

with open(PHYS_PATH,  "r", encoding="utf-8") as f:
    phys = json.load(f)
with open(COSMO_PATH, "r", encoding="utf-8") as f:
    cosmo = json.load(f)

# SSoT constants
N_LEECH    = phys["N_leech"]                                    # 196560
R_S        = cosmo["bao_sound_horizon_mpc"]                     # 147.09
THRESH     = cosmo["bao_sound_horizon_relative_uncertainty"]     # 0.00176803805
ALPHA_BONF = 0.05 / 21                                           # Bonferroni (21 combos)
N_MC       = 100_000
SEED       = 42
MARGIN     = 5

R4 = N_LEECH ** (1.0 / 4.0)

def compute_nmax(scale_val, R, margin=5):
    return max(round(scale_val / R) + margin, 1)

sys.stdout.write("=" * 65 + "\n")
sys.stdout.write("KSAU v34.0 Section B-1 - MC Sensitivity Analysis v2\n")
sys.stdout.write("FIX: Dynamic n_max per sampling range (v33.0 WARNING #1)\n")
sys.stdout.write("=" * 65 + "\n")
sys.stdout.write(f"  N_leech    = {N_LEECH}\n")
sys.stdout.write(f"  R4         = {R4:.6f}\n")
sys.stdout.write(f"  r_s (BAO)  = {R_S} Mpc\n")
sys.stdout.write(f"  THRESH     = {THRESH:.11f} (Planck_sigma, full precision)\n")
sys.stdout.write(f"  N_MC       = {N_MC:,}\n")
sys.stdout.write(f"  seed       = {SEED}\n")
sys.stdout.write(f"  Bonferroni alpha = 0.05/21 = {ALPHA_BONF:.6f}\n")
sys.stdout.write("\n")
sys.stdout.write("n_max (FIX): computed from midpoint of each range (not fixed at r_s)\n")
sys.stdout.write("\n")

# Three ranges for sensitivity analysis
ranges = [
    ("standard [50,500]",   50.0,  500.0),
    ("wide    [30,1000]",   30.0, 1000.0),
    ("narrow  [80,300]",    80.0,  300.0),
]

# Print n_max per range (diagnostic)
sys.stdout.write(f"{'Range':<22}  {'Midpoint':>10}  {'n_max (FIX)':>12}  {'n_max (OLD)':>12}\n")
sys.stdout.write("-" * 62 + "\n")
N_MAX_OLD = compute_nmax(R_S, R4, MARGIN)
for label, rs_min, rs_max in ranges:
    midpoint = (rs_min + rs_max) / 2.0
    n_max_new = compute_nmax(midpoint, R4, MARGIN)
    sys.stdout.write(f"{label:<22}  {midpoint:>10.1f}  {n_max_new:>12d}  {N_MAX_OLD:>12d}\n")
sys.stdout.write("\n")

sys.stdout.write(f"{'Range':<22}  {'RS_MIN':>7}  {'RS_MAX':>7}  {'n_max':>7}  {'hits':>6}  "
                 f"{'MC_p':>8}  {'p<0.05':>7}  {'p<0.0024':>9}  Verdict\n")
sys.stdout.write("-" * 88 + "\n")

results = {}
for label, rs_min, rs_max in ranges:
    # FIXED: dynamic n_max based on range midpoint
    midpoint = (rs_min + rs_max) / 2.0
    n_max_dynamic = compute_nmax(midpoint, R4, MARGIN)

    random.seed(SEED)
    hits = 0
    for _ in range(N_MC):
        rs_rand    = random.uniform(rs_min, rs_max)
        ratio_rand = rs_rand / R4
        n_rand     = round(ratio_rand)
        if 1 <= n_rand <= n_max_dynamic:
            err_rand = abs(ratio_rand - n_rand) / n_rand
            if err_rand <= THRESH:
                hits += 1
    p = hits / N_MC
    results[label] = p
    sig05   = "YES" if p < 0.05        else "no"
    sig0024 = "YES" if p < ALPHA_BONF  else "no"
    verdict = "NOT sig (Bonf)" if p > ALPHA_BONF else "SIGNIFICANT"
    sys.stdout.write(f"{label:<22}  {rs_min:>7.1f}  {rs_max:>7.1f}  {n_max_dynamic:>7d}  {hits:>6d}  "
                     f"{p:>8.5f}  {sig05:>7}  {sig0024:>9}  {verdict}\n")

sys.stdout.write("\n")
sys.stdout.write("--- Sensitivity Summary (FIXED n_max) ---\n")
std_p  = results["standard [50,500]"]
wide_p = results["wide    [30,1000]"]
narr_p = results["narrow  [80,300]"]

sys.stdout.write(f"  standard : p = {std_p:.5f}\n")
sys.stdout.write(f"  wide     : p = {wide_p:.5f}"
                 f"  (delta = {wide_p-std_p:+.5f}, {(wide_p-std_p)/std_p*100:+.1f}%)\n")
sys.stdout.write(f"  narrow   : p = {narr_p:.5f}"
                 f"  (delta = {narr_p-std_p:+.5f}, {(narr_p-std_p)/std_p*100:+.1f}%)\n")
sys.stdout.write(f"  Bonferroni threshold = {ALPHA_BONF:.6f}\n")
sys.stdout.write("\n")

all_not_sig = all(v > ALPHA_BONF for v in [std_p, wide_p, narr_p])
if all_not_sig:
    sys.stdout.write("CONCLUSION: All 3 ranges -> NOT significant after Bonferroni.\n")
    sys.stdout.write("  Main result is robust to sampling range choice.\n")
    sys.stdout.write("  v33.0 WARNING #1 (n_max fix): RESOLVED.\n")
    sys.stdout.write("  Main conclusion unchanged: Bonferroni non-significant across all ranges.\n")
else:
    sys.stdout.write("WARNING: Some ranges show Bonferroni significance.\n")
    sys.stdout.write("  Result IS range-dependent. Requires further investigation.\n")

sys.stdout.write("=" * 65 + "\n")
