#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KSAU v31.0 — Section A: 数値的偵察 (Numerical Patrol)
======================================================
目的:
  N_leech の各種根と宇宙論的スケールの比を系統的に計算し、
  N_leech^{1/4} / r_s ≈ 1/7 の特異性を定量化する。

参照:
  ロードマップ L.70 アプローチ3 (go.md 推奨優先順位1)
  go.md 留保事項1: 探索空間上限の根拠を明記すること
  go.md 留保事項2: 実行環境・SSoT 読み込みを明確にすること

データソース:
  全ての数値定数は SSoT JSON から読み込む
  (E:/Obsidian/KSAU_Project/v6.0/data/)
"""

import sys
import json
import math
import random
from pathlib import Path

# ── SSoT 読み込み ────────────────────────────────────────────────
BASE = Path(__file__).resolve().parent.parent.parent
PHYS_PATH  = BASE / "v6.0" / "data" / "physical_constants.json"
COSMO_PATH = BASE / "v6.0" / "data" / "cosmological_constants.json"

with open(PHYS_PATH, "r", encoding="utf-8") as f:
    phys = json.load(f)
with open(COSMO_PATH, "r", encoding="utf-8") as f:
    cosmo = json.load(f)

print("=" * 60)
print("SSoT 読み込み確認")
print(f"  物理定数ファイル : {PHYS_PATH}")
print(f"  宇宙論定数ファイル: {COSMO_PATH}")
print("=" * 60)

# ── 定数抽出 (SSoT) ──────────────────────────────────────────────
N_LEECH = phys["N_leech"]                          # 196560
R_S     = cosmo["bao_sound_horizon_mpc"]           # 147.09 Mpc (BAO 音響地平線)
H0      = cosmo["H0_planck"]                       # 67.4 km/s/Mpc (Planck 2018)

# ── 宇宙論的スケールの定義 ────────────────────────────────────────
# ハッブル長: c/H0 (Mpc)。c は physical_constants.json の SSoT 値を使用
C_LIGHT_KM_S = phys["c_light_km_s"]               # SSoT から読み込み（NIST/SI 2018 定義値）
D_HUBBLE = C_LIGHT_KM_S / H0                       # ≈ 4450 Mpc (ハッブル長)
D_CMB    = cosmo["cmb_comoving_distance_mpc"]      # CMB 共動距離 [Mpc]（SSoT から読み込み済み）
# REF: Planck 2018 arXiv:1807.06209 Table 2 TT,TE,EE+lowE+lensing: chi_* = 13818.0 Mpc
# NOTE: cosmological_constants.json に格納済み（Session 3 SSoT格納対応）

print()
print("── 宇宙論的スケール (SSoT 値) ──")
print(f"  N_leech           = {N_LEECH}")
print(f"  r_s (BAO)         = {R_S:.4f} Mpc")
print(f"  H0 (Planck)       = {H0:.2f} km/s/Mpc")
print(f"  d_H = c/H0        = {D_HUBBLE:.2f} Mpc  [c = {C_LIGHT_KM_S} km/s, SSoT格納済: NIST/SI定義]")
print(f"  d_CMB (共動距離)   = {D_CMB:.1f} Mpc  [SSoT格納済: Planck 2018 arXiv:1807.06209]")

# ── Step 1: N_leech の各種根の計算 ───────────────────────────────
# 探索する指数 p: N^{1/p} を計算する
# 選択根拠: p = 2, 3, 4, 6, 8, 12, 24 は N_leech の「次元的」根として自然
#   - 1/2: Leech 格子の "面積" スケール
#   - 1/3: 体積スケール
#   - 1/4: 前セッションで使用されたスケール (調査対象)
#   - 1/6, 1/8, 1/12: 格子次元 24 の約数に対応
#   - 1/24: N_leech^{1/24} は最小単位スケール
# 上限 p=24 の根拠: 24 は Leech 格子の次元数であり、これを超える p は
#   物理的動機付けがない (N^{1/p} → 1 as p → ∞)。
EXPONENT_DENOMINATORS = [2, 3, 4, 6, 8, 12, 24]

roots = {}
for p in EXPONENT_DENOMINATORS:
    roots[p] = N_LEECH ** (1.0 / p)

print()
print("── Step 1: N_leech の各種根 ──")
print(f"  N_leech = {N_LEECH}")
print(f"  (注: 上限 p=24 の根拠 = Leech 格子次元数; p > 24 は物理的動機付けなし)")
for p, val in roots.items():
    print(f"  N^{{1/{p}}} = {val:.6f}")

# ── Step 2: 各根と宇宙論スケールの比 ─────────────────────────────
cosmo_scales = {
    "r_s (BAO)  ": R_S,
    "d_H (Hubble)": D_HUBBLE,
    "d_CMB      ": D_CMB,
}

print()
print("── Step 2: 各根 R = N^{1/p} に対する宇宙論スケールとの比 ──")
print(f"  (整数最近傍 n* = round(scale/R) を表示; |err| = |scale/R - n*| / n*)")
print()

header = f"{'p':>4}  {'N^{1/p}':>10}  "
for scale_name in cosmo_scales:
    header += f"{'('+scale_name.strip()+')/R':>14}  "
print(header)
print("-" * (len(header) + 10))

# 結果を収集して後で特異性評価に使う
ratio_table = {}  # ratio_table[p][scale_name] = (ratio, nearest_int, err_frac)

for p, R in roots.items():
    row = f"  {p:>3}  {R:>10.4f}  "
    ratio_table[p] = {}
    for scale_name, scale_val in cosmo_scales.items():
        ratio = scale_val / R
        n_star = round(ratio)
        if n_star == 0:
            n_star = 1
        err_frac = abs(ratio - n_star) / n_star
        ratio_table[p][scale_name] = (ratio, n_star, err_frac)
        row += f"  {ratio:6.3f} (n={n_star:3d}, err={err_frac:.3f})"
    print(row)

# ── Step 3: N^{1/4} / r_s ≈ 1/7 の特異性の定量化 ─────────────────
print()
print("=" * 60)
print("── Step 3: N^{1/4} / r_s ≈ 1/7 の特異性 ──")
R4     = roots[4]
ratio_r4_rs = R_S / R4           # r_s / R4
ratio_r4_7  = R4 * 7             # R4 * 7 との比較 (≈ r_s?)
err_7  = abs(ratio_r4_rs - 7.0) / 7.0

print(f"  R = N^{{1/4}} = {R4:.6f}")
print(f"  r_s / R      = {ratio_r4_rs:.6f}  (≈ 7 ならば r_s ≈ 7 × N^{{1/4}})")
print(f"  7 × R        = {ratio_r4_7:.6f} Mpc  vs  r_s = {R_S:.4f} Mpc")
print(f"  誤差 |ratio - 7| / 7 = {err_7:.4%}")

# ── Step 4: モンテカルロ検定 ─────────────────────────────────────
# 問い: ランダムな宇宙論スケール S ∈ [S_min, S_max] を取ったとき、
#       N^{1/p} × n (任意の整数 n) に err < 観測誤差 以下で近い確率はどれか？
# 今回は「r_s / N^{1/4} が 7 との誤差 ≤ err_obs」の MC 検定を行う
# 帰無仮説 H0: r_s は [50, 500] Mpc のランダム値 → r_s / N^{1/4} が
#              整数 n ∈ [1, 20] のいずれかに err ≤ err_obs 以下で近い

# 探索空間の根拠:
#   n の上限 20: 宇宙論的スケール r_s ≈ 147 Mpc / R4 ≈ 21 なので、
#                n = 20 以上では観測値から外れる。前セッションと一貫性維持。
#   r_s の範囲 [50, 500] Mpc: BAO スケールの理論的範囲
#     (物質密度の変化で ~100-160 Mpc が典型、余裕をもって 50-500 とする)
N_MC        = 10_000
RS_MIN, RS_MAX = 50.0, 500.0
N_STAR_MAX  = 20
ERR_THRESH  = err_7  # 観測された誤差と同程度以下なら「ヒット」

random.seed(42)
hit_count = 0
for _ in range(N_MC):
    rs_rand = random.uniform(RS_MIN, RS_MAX)
    ratio_rand = rs_rand / R4
    # 最近傍整数が [1, N_STAR_MAX] にあり、かつ誤差が閾値以下
    n_rand = round(ratio_rand)
    if 1 <= n_rand <= N_STAR_MAX:
        err_rand = abs(ratio_rand - n_rand) / n_rand
        if err_rand <= ERR_THRESH:
            hit_count += 1

mc_p = hit_count / N_MC

print()
print("── Step 4: モンテカルロ検定 ──")
print(f"  帰無仮説: r_s ~ Uniform[{RS_MIN},{RS_MAX}] Mpc")
print(f"  観測誤差閾値 (err_thresh): {ERR_THRESH:.4%}")
print(f"  整数探索範囲: n ∈ [1, {N_STAR_MAX}]")
print(f"  探索空間上限 n={N_STAR_MAX} の根拠: r_s/R4 ≈ {ratio_r4_rs:.1f} > {N_STAR_MAX} は観測値から逸脱")
print(f"  反復回数: N_MC = {N_MC:,}")
print(f"  ヒット数: {hit_count:,}")
print(f"  MC p 値: {mc_p:.4f}")
if mc_p < 0.05:
    print(f"  → p < 0.05: 統計的有意 (H0 棄却)")
else:
    print(f"  → p = {mc_p:.3f} > 0.05: H0 棄却不能（有意性なし）")

# ── Step 5: 全根 × 全スケールの MC 系統的偵察 ────────────────────
# 「N^{1/4}/r_s ≈ 1/7」と同程度の一致が他の根-スケール組み合わせで
# 偶然起こる確率を系統的に評価し、1/4 乗の特異性を定量化する
print()
print("=" * 60)
print("── Step 5: 系統的偵察 (全根 × 全スケール) ──")
print("  各 (p, scale) 組み合わせの観測誤差 err と MC p 値を計算")
print(f"  (MC 条件: N_MC={N_MC}, 帰無分布 = 各スケール ±50% 範囲, n ∈ [1,{N_STAR_MAX}])")
print()

# 各スケールの「自然な変動範囲」を設定
# r_s: 50-500 Mpc, d_H: 3000-6000 Mpc, d_CMB: 8000-20000 Mpc
scale_ranges = {
    "r_s (BAO)  ": (50.0,   500.0),
    "d_H (Hubble)": (3000.0, 6000.0),
    "d_CMB      ": (8000.0, 20000.0),
}

print(f"  {'p':>4}  {'scale':>14}  {'ratio':>7}  {'n*':>4}  {'err_obs':>8}  {'MC p':>8}  判定")
print("  " + "-" * 62)

survey_results = []
for p, R in roots.items():
    for scale_name, scale_val in cosmo_scales.items():
        ratio = scale_val / R
        n_star = round(ratio)
        if n_star < 1:
            n_star = 1
        err_obs = abs(ratio - n_star) / n_star

        # MC 検定
        s_min, s_max = scale_ranges[scale_name]
        hits = 0
        for _ in range(N_MC):
            s_rand = random.uniform(s_min, s_max)
            r_rand = s_rand / R
            n_r = round(r_rand)
            if 1 <= n_r <= N_STAR_MAX:
                if abs(r_rand - n_r) / n_r <= err_obs:
                    hits += 1
        p_val = hits / N_MC
        sig = "★ p<0.05" if p_val < 0.05 else ""
        survey_results.append((p, scale_name.strip(), ratio, n_star, err_obs, p_val))
        print(f"  {p:>4}  {scale_name:>14}  {ratio:>7.3f}  {n_star:>4d}  {err_obs:>8.4%}  {p_val:>8.4f}  {sig}")
    print()

# ── Step 6: 特異性の定量化 ─────────────────────────────────────
print("=" * 60)
print("── Step 6: 特異性評価サマリー ──")
print()

# err が最小の組み合わせ (最も整数に近い)
best = sorted(survey_results, key=lambda x: x[4])[:5]
print("  [観測誤差 err が最小の組み合わせ Top 5]")
print(f"  {'p':>4}  {'scale':>14}  {'ratio':>7}  {'n*':>4}  {'err_obs':>8}  {'MC p':>8}")
print("  " + "-" * 55)
for rec in best:
    p, sn, ratio, ns, err, pv = rec
    mark = " ← N^{1/4}/r_s ≈ 7" if p == 4 and "BAO" in sn else ""
    print(f"  {p:>4}  {sn:>14}  {ratio:>7.3f}  {ns:>4d}  {err:>8.4%}  {pv:>8.4f}{mark}")

print()
# p=4, r_s の順位を特定
all_sorted = sorted(survey_results, key=lambda x: x[4])
rank_14_rs = next((i+1 for i, r in enumerate(all_sorted) if r[0]==4 and "BAO" in r[1]), None)
total = len(all_sorted)
print(f"  N^{{1/4}}/r_s ≈ 7 の組み合わせ:")
print(f"    誤差ランク: {rank_14_rs} / {total}  (誤差が小さい順)")

# MC p が最小の組み合わせ
best_p = sorted(survey_results, key=lambda x: x[5])[:5]
print()
print("  [MC p 値が最小の組み合わせ Top 5]")
print(f"  {'p':>4}  {'scale':>14}  {'ratio':>7}  {'n*':>4}  {'err_obs':>8}  {'MC p':>8}")
print("  " + "-" * 55)
for rec in best_p:
    p, sn, ratio, ns, err, pv = rec
    mark = " ← N^{1/4}/r_s ≈ 7" if p == 4 and "BAO" in sn else ""
    print(f"  {p:>4}  {sn:>14}  {ratio:>7.3f}  {ns:>4d}  {err:>8.4%}  {pv:>8.4f}{mark}")

# ── Step 7: 1/4 乗の「幾何学的特異性」評価 ────────────────────────
print()
print("=" * 60)
print("── Step 7: N^{1/4} の選択について ──")
print()
print("  [観点A] Leech 格子の構造との対応:")
print(f"    N_leech = {N_LEECH} = 2^4 × 3^3 × 5 × 7 × 13")
print(f"    N^{{1/2}} = {roots[2]:.4f}  (格子の 2D 面積スケール)")
print(f"    N^{{1/3}} = {roots[3]:.4f}  (格子の 3D 体積スケール)")
print(f"    N^{{1/4}} = {roots[4]:.4f}  (4D ヒッパーキューブ対角スケール)")
print(f"    N^{{1/6}} = {roots[6]:.4f}  (6D スケール)")
print(f"    N^{{1/8}} = {roots[8]:.4f}  (8D = E_8 次元スケール)")
print(f"    N^{{1/12}}= {roots[12]:.4f} (12D スケール)")
print(f"    N^{{1/24}}= {roots[24]:.6f} (24D = Leech 格子次元スケール)")
print()
print("  [観点B] R_cell の定義との整合性:")
R_cell = cosmo.get("R_cell", None)
R_cell_origin = cosmo.get("R_cell_origin", "未定義")
if R_cell:
    print(f"    R_cell = {R_cell:.4f} Mpc (SSoT 値)")
    print(f"    定義: {R_cell_origin[:80]}...")
    print(f"    R_cell / N^{{1/4}} = {R_cell / roots[4]:.6f}")
    # R_cell = N^{1/4} / (1 + alpha*beta)
    alpha_val = cosmo.get("alpha", 1/48)
    beta_val  = cosmo.get("beta_ssot", None)
    if beta_val:
        denom = 1 + alpha_val * beta_val
        R_cell_formula = roots[4] / denom
        print(f"    N^{{1/4}}/(1+α×β) = {R_cell_formula:.4f} Mpc  (α={alpha_val:.6f}, β={beta_val:.6f})")
        print(f"    → SSoT 定義との一致: {abs(R_cell_formula - R_cell)/R_cell:.6%} 誤差")
print()
print("  [観点C] 4 乗根の物理的意味 (暫定解釈):")
print("    M 理論の時空次元: 11D = 4D (観測) + 7D (コンパクト)")
print("    4 乗根 = '4 次元観測者が見る 1/4 の次元スケール' という解釈は可能だが、")
print("    これは事後的動機付けであり、Co_0 の表現論からの必然性はない。")
print()
print("  ★ 結論: N^{1/4} の選択は数値的便宜によるものと判断するのが誠実。")
print("    ただし R_cell の定義 (SSoT) が N^{1/4} に基づいているため、")
print("    N^{1/4} は KSAU フレームワーク内での '約束ごと' として機能している。")

# ── 最終評価 ──────────────────────────────────────────────────────
print()
print("=" * 60)
print("── 最終評価: Section A ステータス ──")
print()
p4_rs_rec = next((r for r in survey_results if r[0]==4 and "BAO" in r[1]), None)
if p4_rs_rec:
    _, _, ratio_val, ns_val, err_val, pv_val = p4_rs_rec
    print(f"  N^{{1/4}} / r_s ≈ 1/7 の観測:")
    print(f"    比率 r_s / N^{{1/4}} = {ratio_val:.4f}")
    print(f"    最近傍整数 n* = {ns_val}")
    print(f"    観測誤差 err = {err_val:.4%}")
    print(f"    MC p 値 = {pv_val:.4f}")
    if pv_val < 0.05:
        verdict = "MOTIVATED_SIGNIFICANT (代数的根拠は依然未構築)"
    else:
        verdict = "UNMOTIVATED — 統計的有意性なし。代数的根拠も未構築。"
    print(f"  → ステータス: {verdict}")

rank_14_rs_pval = next(
    (i+1 for i, r in enumerate(sorted(survey_results, key=lambda x: x[5]))
     if r[0]==4 and "BAO" in r[1]), None
)
print()
print(f"  参考: {total} 通りの (根, スケール) 組み合わせ中、")
print(f"    N^{{1/4}}/r_s の MC p 値順位: {rank_14_rs_pval} / {total}")
print(f"    N^{{1/4}}/r_s の err 順位   : {rank_14_rs} / {total}")
print()
print("  ★ 1/4 乗の特異性:")
if rank_14_rs <= total // 4:
    print(f"    err ランク {rank_14_rs}/{total}: 上位 25% 以内 → 相対的に良好な一致だが偶然排除不能")
else:
    print(f"    err ランク {rank_14_rs}/{total}: 上位 25% を超える → 特段の特異性なし")

print()
print("  ★ Section A の総括:")
print("    (1) MC p 値の結果に基づき、統計的ステータスを更新する。")
print("    (2) N^{1/4} の選択に対する Co_0 / 表現論的根拠は依然として未構築。")
print("    (3) R_cell の SSoT 定義が N^{1/4} を参照しているため、")
print("        フレームワーク内での一貫性は確保されているが、")
print("        それは独立した証拠ではなく循環参照に近い。")
print()
print("=" * 60)
print("  Section A 数値的偵察: 完了")
print("=" * 60)
