#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KSAU v33.0 - Task A: ERR_THRESH 循環閾値の解消
================================================
目的:
  v31.0/v32.0 で継続してきた技術的負債 [負債 #1] を解消する。
  ERR_THRESH = err_7（観測値自身が有意性の閾値）という循環を排除し、
  独立な根拠に基づく閾値での MC 再実行を行い、バイアス方向を定量化する。

対応方針（v33.0 Roadmap Task A より）:
  (a) 計測誤差の公式不確かさ: Planck 2018 σ_{r_s} = 0.26 Mpc → 相対誤差 0.1768%
  (b) 先験的許容誤差: 1%, 5%, 10%（観測データ非依存）
  (c) SSoT 格納: 閾値を cosmological_constants.json に格納済み

SSoT: 全定数を v6.0/data/*.json から読み込む。
"""

import sys
import json
import math
import random
from pathlib import Path

# ── SSoT 読み込み ──────────────────────────────────────────────────────────
BASE       = Path(__file__).resolve().parent.parent
PHYS_PATH  = BASE / "v6.0" / "data" / "physical_constants.json"
COSMO_PATH = BASE / "v6.0" / "data" / "cosmological_constants.json"

with open(PHYS_PATH,  "r", encoding="utf-8") as f:
    phys  = json.load(f)
with open(COSMO_PATH, "r", encoding="utf-8") as f:
    cosmo = json.load(f)

print("=" * 70)
print("KSAU v33.0 - Task A: ERR_THRESH 循環閾値の解消")
print("=" * 70)
print(f"  SSoT [phys] : {PHYS_PATH}")
print(f"  SSoT [cosmo]: {COSMO_PATH}")

# ── 定数抽出（SSoT）────────────────────────────────────────────────────────
N_LEECH      = phys["N_leech"]                            # 196560
R_S          = cosmo["bao_sound_horizon_mpc"]             # 147.09 Mpc
SIGMA_RS     = cosmo["bao_sound_horizon_uncertainty_mpc"] # 0.26 Mpc  ← Planck 2018
REL_SIGMA_RS = cosmo["bao_sound_horizon_relative_uncertainty"]  # 0.1768%
RS_REF       = cosmo["bao_sound_horizon_ref"]
H0           = cosmo["H0_planck"]                         # 67.4 km/s/Mpc
C_LIGHT_KM_S = phys["c_light_km_s"]                      # 299792.458 km/s
D_HUBBLE     = C_LIGHT_KM_S / H0                          # ~4448 Mpc
D_CMB        = cosmo["cmb_comoving_distance_mpc"]         # 13818.0 Mpc

# KSAU 観測値
R4           = N_LEECH ** (1.0 / 4.0)                    # N^{1/4} ≈ 21.0559
ratio_r4_rs  = R_S / R4                                   # r_s / R4 ≈ 6.9857
ERR_7_CIRC   = abs(ratio_r4_rs - 7.0) / 7.0              # 循環閾値（旧: 0.2044%）

print()
print("── 観測値（SSoT）──────────────────────────────────────────────────")
print(f"  N_leech              = {N_LEECH}")
print(f"  R4 = N^{{1/4}}        = {R4:.6f}")
print(f"  r_s (BAO)            = {R_S:.4f} Mpc")
print(f"  σ_{{r_s}} (Planck2018) = {SIGMA_RS:.4f} Mpc  [{RS_REF}]")
print(f"  相対不確かさ σ/r_s   = {REL_SIGMA_RS:.4%}")
print(f"  r_s / R4             = {ratio_r4_rs:.6f}  (target: ~7)")
print(f"  err_7 (循環, 旧値)   = {ERR_7_CIRC:.4%}")

# ── 閾値の設定 ─────────────────────────────────────────────────────────────
#   (a) Planck 2018 公式不確かさ由来（独立）
#   (b) 先験的許容誤差（観測非依存）
THRESHOLDS = {
    "CIRCULAR (旧v31/32)":     ERR_7_CIRC,   # 循環参照（比較用のみ）
    "Planck_sigma (独立)":     REL_SIGMA_RS,  # (a) Planck 2018 σ_{r_s}/r_s
    "apriori_1pct":            0.01,          # (b) 先験的 1%
    "apriori_5pct":            0.05,          # (b) 先験的 5%
    "apriori_10pct":           0.10,          # (b) 先験的 10%
}

print()
print("── 閾値一覧 ─────────────────────────────────────────────────────────")
print(f"  {'閾値名':<28}  {'相対誤差 (%)':>12}  根拠")
print("  " + "-" * 65)
print(f"  {'CIRCULAR (旧v31/32) [参照のみ]':<28}  {ERR_7_CIRC*100:>11.4f}%  観測値 err_7 自身（循環）")
print(f"  {'Planck_sigma (a)':<28}  {REL_SIGMA_RS*100:>11.4f}%  Planck 2018 σ/r_s（独立）")
print(f"  {'apriori_1pct (b)':<28}  {1.0:>11.4f}%  先験的 1%（観測非依存）")
print(f"  {'apriori_5pct (b)':<28}  {5.0:>11.4f}%  先験的 5%（観測非依存）")
print(f"  {'apriori_10pct (b)':<28}  {10.0:>11.4f}%  先験的 10%（観測非依存）")

# ── MC パラメータ ──────────────────────────────────────────────────────────
N_MC           = 100_000   # 精度向上のため v32.0 の 10x
RS_MIN, RS_MAX = 50.0, 500.0
SEED           = 42
MARGIN         = 5         # n_max = round(scale/R) + margin（v32.0 継承）

def compute_nmax(scale_nominal: float, R: float, margin: int = 5) -> int:
    return max(round(scale_nominal / R) + margin, 1)

N_MAX_DYN_RS = compute_nmax(R_S, R4, MARGIN)  # ~12（v32.0 と同一）

print()
print("── MC 設定 ──────────────────────────────────────────────────────────")
print(f"  N_MC          = {N_MC:,}")
print(f"  r_s range     = [{RS_MIN}, {RS_MAX}] Mpc  (帰無仮説: Uniform)")
print(f"  seed          = {SEED}")
print(f"  n_max (R4,rs) = {N_MAX_DYN_RS}  (dynamic: round({R_S:.2f}/{R4:.4f}) + {MARGIN})")

# ── Step 1: N^{1/4}/r_s 単独 MC（閾値比較）────────────────────────────────
print()
print("=" * 70)
print("── Step 1: N^{1/4}/r_s 単独 MC（5閾値比較）────────────────────────")
print(f"  検定統計量: r_s/R4 ~= {ratio_r4_rs:.6f},  n* = 7")
print()

single_results = {}
random.seed(SEED)

for thresh_name, thresh_val in THRESHOLDS.items():
    random.seed(SEED)
    hits = 0
    for _ in range(N_MC):
        rs_rand    = random.uniform(RS_MIN, RS_MAX)
        ratio_rand = rs_rand / R4
        n_rand     = round(ratio_rand)
        if 1 <= n_rand <= N_MAX_DYN_RS:
            err_rand = abs(ratio_rand - n_rand) / n_rand
            if err_rand <= thresh_val:
                hits += 1
    p_val = hits / N_MC
    single_results[thresh_name] = p_val

print(f"  {'閾値名':<28}  {'閾値':>8}  {'hits':>7}  {'MC p':>8}  p<0.05?  p<0.0024?")
print("  " + "-" * 72)
for thresh_name, thresh_val in THRESHOLDS.items():
    p_val = single_results[thresh_name]
    random.seed(SEED)
    hits_recalc = 0
    for _ in range(N_MC):
        rs_rand    = random.uniform(RS_MIN, RS_MAX)
        ratio_rand = rs_rand / R4
        n_rand     = round(ratio_rand)
        if 1 <= n_rand <= N_MAX_DYN_RS:
            err_rand = abs(ratio_rand - n_rand) / n_rand
            if err_rand <= thresh_val:
                hits_recalc += 1
    sig_05   = "YES" if p_val < 0.05    else "no"
    sig_bonf = "YES" if p_val < 0.0024  else "no"
    is_circ  = " [循環]" if "CIRCULAR" in thresh_name else ""
    print(f"  {thresh_name:<28}  {thresh_val*100:>7.4f}%  {hits_recalc:>7d}  {p_val:>8.5f}  {sig_05:<7}  {sig_bonf}{is_circ}")

# ── Step 2: 全体系的サーベイ（Planck_sigma 閾値のみ独立実行）──────────────
print()
print("=" * 70)
print("── Step 2: 系統的サーベイ（Planck_sigma 閾値, 全 root × 全 scale）")
print(f"  N_MC={N_MC:,}, threshold = Planck_sigma = {REL_SIGMA_RS:.4%}")
print()

EXPONENT_DENOMINATORS = [2, 3, 4, 6, 8, 12, 24]
roots = {p: N_LEECH ** (1.0 / p) for p in EXPONENT_DENOMINATORS}

cosmo_scales = {
    "r_s (BAO)":    (R_S,     50.0,   500.0),
    "d_H (Hubble)": (D_HUBBLE, 3000.0, 6000.0),
    "d_CMB":        (D_CMB,   8000.0, 20000.0),
}

print(f"  {'p':>4}  {'scale':>14}  {'ratio':>8}  {'n*':>4}  {'nmax':>5}  "
      f"{'err_obs':>8}  {'MC_p(Planck_σ)':>15}  sig")
print("  " + "-" * 80)

survey_planck = []
for p, R in roots.items():
    for scale_name, (scale_val, s_min, s_max) in cosmo_scales.items():
        ratio   = scale_val / R
        n_star  = max(round(ratio), 1)
        err_obs = abs(ratio - n_star) / n_star
        n_max_d = compute_nmax(scale_val, R, MARGIN)
        thresh  = REL_SIGMA_RS   # 独立な閾値 (Planck_sigma)

        random.seed(SEED)
        hits = 0
        for _ in range(N_MC):
            s_rand = random.uniform(s_min, s_max)
            r_rand = s_rand / R
            n_r    = round(r_rand)
            if 1 <= n_r <= n_max_d:
                if abs(r_rand - n_r) / n_r <= thresh:
                    hits += 1
        p_val = hits / N_MC
        sig   = "* p<0.05" if p_val < 0.05 else ""
        survey_planck.append((p, scale_name, ratio, n_star, n_max_d, err_obs, p_val))
        print(f"  {p:>4}  {scale_name:>14}  {ratio:>8.3f}  {n_star:>4d}  {n_max_d:>5d}  "
              f"{err_obs:>8.4%}  {p_val:>15.5f}  {sig}")
    print()

# ── Step 3: Bonferroni 補正（Planck_sigma） ─────────────────────────────────
print("=" * 70)
print("── Step 3: Bonferroni 補正（Planck_sigma 閾値）────────────────────")
n_tests_s = len(survey_planck)
alpha_bonf = 0.05 / n_tests_s
print(f"  n_tests         = {n_tests_s}")
print(f"  alpha_corrected = 0.05 / {n_tests_s} = {alpha_bonf:.6f}")

sig_bonf_planck = [r for r in survey_planck if r[6] < alpha_bonf]
print(f"  Bonferroni-significant: {len(sig_bonf_planck)}")
if sig_bonf_planck:
    for rec in sig_bonf_planck:
        p, sn, ratio, ns, nm, ev, pv = rec
        print(f"    p={p}, scale={sn}, MC_p={pv:.5f} < {alpha_bonf:.6f} ← SIGNIFICANT")
else:
    print("  → 全21組み合わせで Bonferroni 補正後有意なし")

# N^{1/4}/r_s エントリの詳細
p4_rs = next((r for r in survey_planck if r[0] == 4 and "BAO" in r[1]), None)
if p4_rs:
    p_, sn_, ratio_, ns_, nm_, ev_, pv_ = p4_rs
    print()
    print(f"  【N^{{1/4}}/r_s エントリ（主結果）】")
    print(f"    ratio    = {ratio_:.6f}")
    print(f"    err_obs  = {ev_:.4%}  (vs Planck_sigma = {REL_SIGMA_RS:.4%})")
    print(f"    MC p (Planck_sigma) = {pv_:.5f}")
    print(f"    Bonferroni 閾値     = {alpha_bonf:.6f}")
    if pv_ < alpha_bonf:
        print(f"    → SIGNIFICANT after Bonferroni")
    else:
        print(f"    → NOT significant after Bonferroni")

# ── Step 4: バイアス方向の定量化 ─────────────────────────────────────────
print()
print("=" * 70)
print("── Step 4: バイアス方向の定量化（循環 vs 独立 閾値の比較）─────────")
print()
print(f"  N^{{1/4}}/r_s 検定（Step 1結果）:")
print(f"  {'閾値名':<28}  {'閾値':>8}  {'MC p':>8}  バイアス評価")
print("  " + "-" * 68)

p_circ  = single_results["CIRCULAR (旧v31/32)"]
p_planck= single_results["Planck_sigma (独立)"]
p_1pct  = single_results["apriori_1pct"]
p_5pct  = single_results["apriori_5pct"]
p_10pct = single_results["apriori_10pct"]

def bias_direction(p_old, p_new, thresh_old, thresh_new):
    """循環閾値と比較したバイアス方向を評価"""
    if thresh_new < thresh_old:
        direction = "閾値縮小: p ↑ (検定厳化)"
    elif thresh_new > thresh_old:
        direction = "閾値拡大: p ↓ (検定緩和)"
    else:
        direction = "同一閾値"
    return direction

rows = [
    ("CIRCULAR (旧v31/32)", ERR_7_CIRC,   p_circ,  "基準（循環）"),
    ("Planck_sigma (独立)", REL_SIGMA_RS, p_planck, bias_direction(p_circ, p_planck, ERR_7_CIRC, REL_SIGMA_RS)),
    ("apriori_1pct",        0.01,          p_1pct,  bias_direction(p_circ, p_1pct,  ERR_7_CIRC, 0.01)),
    ("apriori_5pct",        0.05,          p_5pct,  bias_direction(p_circ, p_5pct,  ERR_7_CIRC, 0.05)),
    ("apriori_10pct",       0.10,          p_10pct, bias_direction(p_circ, p_10pct, ERR_7_CIRC, 0.10)),
]
for name, thresh, p, bias in rows:
    circ_mark = " [参照]" if "CIRCULAR" in name else ""
    print(f"  {name:<28}  {thresh*100:>7.4f}%  {p:>8.5f}  {bias}{circ_mark}")

print()
print("  【バイアス定量化サマリ】")
print(f"  循環閾値 ERR_THRESH = {ERR_7_CIRC:.4%} の場合の MC p = {p_circ:.5f}")
print(f"  Planck_sigma (独立) = {REL_SIGMA_RS:.4%} の場合の MC p = {p_planck:.5f}")
delta_pct = (p_planck - p_circ) / p_circ * 100 if p_circ > 0 else float('nan')
print(f"  Δp = {p_planck - p_circ:+.5f}  ({delta_pct:+.1f}% 相対変化)")

if REL_SIGMA_RS < ERR_7_CIRC:
    print(f"  → 循環閾値は Planck_sigma より {(ERR_7_CIRC/REL_SIGMA_RS - 1)*100:.1f}% 緩い閾値だった。")
    print(f"     独立な閾値採用により p 値は上昇 → 旧閾値は p 値を過小評価していた（バイアスあり）。")
elif REL_SIGMA_RS > ERR_7_CIRC:
    print(f"  → 循環閾値は Planck_sigma より {(1 - ERR_7_CIRC/REL_SIGMA_RS)*100:.1f}% 厳しい閾値だった。")
    print(f"     独立な閾値採用により p 値は低下 → 旧閾値は p 値を過大評価していた方向。")
else:
    print(f"  → 循環閾値と Planck_sigma が一致（バイアスなし）。")

# ── Step 5: 最終判定 ──────────────────────────────────────────────────────
print()
print("=" * 70)
print("── Step 5: Task A 最終判定 ─────────────────────────────────────────")
print()

all_thresholds_not_significant = True
threshold_verdicts = {}
for name, thresh in THRESHOLDS.items():
    p = single_results[name]
    bonf_sig = p < 0.0024  # Bonferroni 閾値（近似: 0.05/21）
    threshold_verdicts[name] = bonf_sig
    if "CIRCULAR" not in name and bonf_sig:
        all_thresholds_not_significant = False

print(f"  独立閾値での Bonferroni 補正後有意性（α/21 ≈ 0.0024）:")
for name, bonf_sig in threshold_verdicts.items():
    if "CIRCULAR" in name:
        label = "  [参照] "
    else:
        label = "  [独立] "
    verdict = "SIGNIFICANT" if bonf_sig else "not significant"
    print(f"  {label}{name:<28}: {verdict}")

print()
if all_thresholds_not_significant:
    print("  ✅ Task A 主結論: 全独立閾値で Bonferroni 補正後有意なし")
    print("     → 循環閾値解消後も N^{1/4}/r_s ≈ 7 の統計的有意性は確認されない。")
    print("     → v31.0/v32.0 の主結論（Bonferroni 補正後 p > 0.0024）は堅牢。")
    verdict_str = "NOT SIGNIFICANT (独立閾値全て)"
else:
    print("  ⚠️  Task A 主結論: 一部独立閾値で Bonferroni 補正後有意")
    print("     → 閾値依存性あり。詳細な解釈が必要。")
    verdict_str = "THRESHOLD DEPENDENT"

print()
print(f"  ERR_THRESH 循環: 解消完了")
print(f"  新閾値 SSoT 格納: 完了（cosmological_constants.json 更新済み）")
print(f"  MC 再実行: 完了（N_MC={N_MC:,}）")
print(f"  バイアス定量化: 完了")
print()
print(f"  Task A 成功基準:")
print(f"    [x] 独立な根拠に基づく閾値設定完了（Planck 2018 σ_rs + 先験的閾値）")
print(f"    [x] 新閾値での MC 再実行完了（N_MC={N_MC:,}）")
print(f"    [x] バイアス方向の定量化完了")
print(f"    [x] 新結論明記: {verdict_str}")
print()
print("  *** Task A: COMPLETED ***")
print("=" * 70)
