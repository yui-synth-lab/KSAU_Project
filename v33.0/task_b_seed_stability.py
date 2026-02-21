#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KSAU v33.0 - Task B: MC 乱数シード安定性検証
=============================================
目的:
  random.seed(42) 固定で再現性は確保されているが、
  特定のシードが結果に有利に働いていないかを確認する。

方針（v33.0 Roadmap Task B より）:
  - 複数シード（0, 1, 7, 42, 100, 314）で MC 再実行
  - 各シードでの p 値分布を記録
  - 結果の安定性（標準偏差、max-min 差）を定量化

成功基準:
  複数シードで p 値が一貫して p > 0.0024（Bonferroni 補正後）であることを確認。

SSoT: 全定数を v6.0/data/*.json から読み込む。
Task A の独立閾値（Planck_sigma）を使用。
"""

import json
import math
import random
import statistics
from pathlib import Path

# -- SSoT 読み込み --
BASE       = Path(__file__).resolve().parent.parent
PHYS_PATH  = BASE / "v6.0" / "data" / "physical_constants.json"
COSMO_PATH = BASE / "v6.0" / "data" / "cosmological_constants.json"

with open(PHYS_PATH,  "r", encoding="utf-8") as f:
    phys  = json.load(f)
with open(COSMO_PATH, "r", encoding="utf-8") as f:
    cosmo = json.load(f)

print("=" * 70)
print("KSAU v33.0 - Task B: MC 乱数シード安定性検証")
print("=" * 70)
print(f"  SSoT [phys] : {PHYS_PATH}")
print(f"  SSoT [cosmo]: {COSMO_PATH}")

# -- 定数抽出（SSoT）--
N_LEECH      = phys["N_leech"]
R_S          = cosmo["bao_sound_horizon_mpc"]
REL_SIGMA_RS = cosmo["bao_sound_horizon_relative_uncertainty"]  # Task A で格納済み
H0           = cosmo["H0_planck"]
C_LIGHT_KM_S = phys["c_light_km_s"]
D_HUBBLE     = C_LIGHT_KM_S / H0
D_CMB        = cosmo["cmb_comoving_distance_mpc"]

R4           = N_LEECH ** (1.0 / 4.0)
err_7_circ   = abs(R_S / R4 - 7.0) / 7.0   # 参照用（循環）

EXPONENT_DENOMINATORS = [2, 3, 4, 6, 8, 12, 24]
roots = {p: N_LEECH ** (1.0 / p) for p in EXPONENT_DENOMINATORS}

cosmo_scales = {
    "r_s (BAO)":    (R_S,     50.0,   500.0),
    "d_H (Hubble)": (D_HUBBLE, 3000.0, 6000.0),
    "d_CMB":        (D_CMB,   8000.0, 20000.0),
}

MARGIN = 5
def compute_nmax(scale_val: float, R: float, margin: int = 5) -> int:
    return max(round(scale_val / R) + margin, 1)

print()
print(f"  N_leech           = {N_LEECH}")
print(f"  R4 = N^{{1/4}}     = {R4:.6f}")
print(f"  r_s               = {R_S:.4f} Mpc")
print(f"  Planck_sigma閾値  = {REL_SIGMA_RS:.4%}  (Task A SSoT格納済)")
print(f"  循環閾値(参照)    = {err_7_circ:.4%}  (v31/32 ERR_THRESH)")

# -- MC 設定 --
N_MC        = 50_000   # 各シードで高速に
SEEDS       = [0, 1, 7, 42, 100, 314]
# 二種類の閾値で検証（Planck_sigma + 循環）
THRESH_PLANCK = REL_SIGMA_RS
THRESH_CIRC   = err_7_circ

print()
print(f"  N_MC = {N_MC:,}  (per seed)")
print(f"  Seeds = {SEEDS}")
print(f"  Bonferroni alpha = 0.05 / 21 = {0.05/21:.6f}")

# -- Step 1: N^{1/4}/r_s 単独検定・複数シード --
print()
print("=" * 70)
print("-- Step 1: N^{1/4}/r_s 単独検定（複数シード）──────────────────────")
print(f"  n_max = {compute_nmax(R_S, R4, MARGIN)}")
print()
N_MAX_RS = compute_nmax(R_S, R4, MARGIN)

p_vals_planck = []
p_vals_circ   = []

print(f"  {'Seed':>5}  {'p(Planck_sigma)':>16}  {'p(CIRCULAR)':>12}  p<0.05(P)?  p<0.0024(P)?")
print("  " + "-" * 62)

for seed in SEEDS:
    random.seed(seed)
    hits_p = 0
    hits_c = 0
    for _ in range(N_MC):
        rs_rand    = random.uniform(50.0, 500.0)
        ratio_rand = rs_rand / R4
        n_rand     = round(ratio_rand)
        if 1 <= n_rand <= N_MAX_RS:
            err_rand = abs(ratio_rand - n_rand) / n_rand
            if err_rand <= THRESH_PLANCK:
                hits_p += 1
            if err_rand <= THRESH_CIRC:
                hits_c += 1
    p_p = hits_p / N_MC
    p_c = hits_c / N_MC
    p_vals_planck.append(p_p)
    p_vals_circ.append(p_c)
    sig05   = "YES" if p_p < 0.05   else "no"
    sig0024 = "YES" if p_p < 0.0024 else "no"
    print(f"  {seed:>5}  {p_p:>16.5f}  {p_c:>12.5f}  {sig05:<10}  {sig0024}")

print()
print(f"  Planck_sigma 閾値:")
print(f"    mean = {statistics.mean(p_vals_planck):.5f}")
print(f"    std  = {statistics.stdev(p_vals_planck):.5f}")
print(f"    min  = {min(p_vals_planck):.5f}")
print(f"    max  = {max(p_vals_planck):.5f}")
print(f"    range= {max(p_vals_planck) - min(p_vals_planck):.5f}")
print(f"  CIRCULAR 閾値（参照）:")
print(f"    mean = {statistics.mean(p_vals_circ):.5f}")
print(f"    std  = {statistics.stdev(p_vals_circ):.5f}")
print(f"    min  = {min(p_vals_circ):.5f}")
print(f"    max  = {max(p_vals_circ):.5f}")

# -- Step 2: 全21組み合わせ・複数シード（主要チェック: seed=42 vs others）--
print()
print("=" * 70)
print("-- Step 2: 全21組み合わせ・複数シード p値安定性サーベイ ─────────────")
print(f"  閾値: Planck_sigma = {THRESH_PLANCK:.4%}, N_MC = {N_MC:,}")
print()

# 各 (p, scale) エントリについて、全シードでの p 値
all_entries = []
for p_exp, R in roots.items():
    for scale_name, (scale_val, s_min, s_max) in cosmo_scales.items():
        ratio   = scale_val / R
        n_star  = max(round(ratio), 1)
        err_obs = abs(ratio - n_star) / n_star
        n_max_d = compute_nmax(scale_val, R, MARGIN)
        all_entries.append((p_exp, scale_name, ratio, n_star, n_max_d, err_obs, s_min, s_max, R))

ALPHA_BONF = 0.05 / len(all_entries)

print(f"  {'p':>4}  {'scale':>14}  {'ratio':>8}  "
      f"  p(s=42)  p(s=0)   p(s=7)   p_mean   p_std    Bonf?")
print("  " + "-" * 85)

seed_pvalues = {seed: [] for seed in SEEDS}
entry_results = []

for entry in all_entries:
    p_exp, scale_name, ratio, n_star, n_max_d, err_obs, s_min, s_max, R = entry
    per_seed_p = {}
    for seed in SEEDS:
        random.seed(seed)
        hits = 0
        for _ in range(N_MC):
            s_rand = random.uniform(s_min, s_max)
            r_rand = s_rand / R
            n_r    = round(r_rand)
            if 1 <= n_r <= n_max_d:
                if abs(r_rand - n_r) / n_r <= THRESH_PLANCK:
                    hits += 1
        p_val = hits / N_MC
        per_seed_p[seed] = p_val
        seed_pvalues[seed].append(p_val)

    pvals_list = list(per_seed_p.values())
    p_mean = statistics.mean(pvals_list)
    p_std  = statistics.stdev(pvals_list) if len(pvals_list) > 1 else 0.0
    bonf_sig = "BONF!" if p_mean < ALPHA_BONF else ""
    entry_results.append((p_exp, scale_name, ratio, n_star, per_seed_p, p_mean, p_std))

    print(f"  {p_exp:>4}  {scale_name:>14}  {ratio:>8.3f}  "
          f"  {per_seed_p[42]:>.5f}  {per_seed_p[0]:>.5f}  {per_seed_p[7]:>.5f}  "
          f"{p_mean:>.5f}  {p_std:>.5f}  {bonf_sig}")

# -- Step 3: 集計 --
print()
print("=" * 70)
print("-- Step 3: シード安定性サマリ ──────────────────────────────────────")
print()
print(f"  Bonferroni 閾値: {ALPHA_BONF:.6f}  (0.05/{len(all_entries)})")
print()

bonf_violated_any = [e for e in entry_results if min(e[4].values()) < ALPHA_BONF]
print(f"  Bonferroni 有意（全シードの min p < {ALPHA_BONF:.6f}）: "
      f"{len(bonf_violated_any)}/{len(entry_results)} エントリ")

print()
print(f"  シード別 p 値統計（N^{{1/4}}/r_s エントリ, p=4, scale=r_s(BAO)）:")
target_entry = next((e for e in entry_results if e[0]==4 and "BAO" in e[1]), None)
if target_entry:
    p_exp_, sn_, ratio_, ns_, per_seed_p_, p_mean_, p_std_ = target_entry
    print(f"    {'Seed':>5}  {'MC p':>8}")
    for seed in SEEDS:
        print(f"    {seed:>5}  {per_seed_p_[seed]:>8.5f}")
    print(f"    {'mean':>5}  {p_mean_:>8.5f}")
    print(f"    {'std':>5}  {p_std_:>8.5f}")
    print(f"    {'range':>5}  {max(per_seed_p_.values()) - min(per_seed_p_.values()):>8.5f}")
    all_above_bonf = all(v > ALPHA_BONF for v in per_seed_p_.values())
    if all_above_bonf:
        print(f"    -> 全シードで Bonferroni 補正後有意なし (p > {ALPHA_BONF:.6f})")
    else:
        print(f"    -> 一部シードで Bonferroni 補正後有意")

# -- Step 4: 最終判定 --
print()
print("=" * 70)
print("-- Step 4: Task B 最終判定 ─────────────────────────────────────────")
print()

# N^{1/4}/r_s の主エントリ全シード確認
if target_entry:
    all_not_sig = all(v > ALPHA_BONF for v in per_seed_p_.values())
    if all_not_sig:
        print("  N^{1/4}/r_s エントリ（p=4, r_s(BAO)）:")
        print(f"    全 {len(SEEDS)} シードで Bonferroni 補正後有意なし")
        print(f"    シード間 p 値の範囲: {min(per_seed_p_.values()):.5f} - {max(per_seed_p_.values()):.5f}")
        print(f"    std = {p_std_:.5f}  (安定)")
        print()

if not bonf_violated_any:
    print("  ✅ Task B 主結論: 全21組み合わせ × 全6シードで Bonferroni 補正後有意なし")
    print("     → seed=42 が結果に有利に働いていた証拠なし")
    print("     → v31.0/v32.0 の主結論は複数シードで堅牢（シード依存性なし）")
else:
    print(f"  ⚠️  Task B: {len(bonf_violated_any)} エントリで一部シード Bonferroni 有意")
    for e in bonf_violated_any:
        print(f"     p={e[0]}, scale={e[1]}: min p={min(e[4].values()):.5f}")

print()
print("  Task B 成功基準:")
print("    [x] 複数シード（0, 1, 7, 42, 100, 314）で MC 再実行")
print("    [x] 各シードでの p 値を記録")
print("    [x] 結果の安定性（std, range）を定量化")
if not bonf_violated_any:
    print("    [x] 全シードで p > 0.0024（Bonferroni 補正後）を確認")
    print()
    print("  *** Task B: COMPLETED ***")
else:
    print("    [!] 一部シードで p < 0.0024 → 詳細調査が必要")
    print()
    print("  *** Task B: CONDITIONAL COMPLETED (例外記録) ***")
print("=" * 70)
