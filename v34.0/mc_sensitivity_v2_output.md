# mc_sensitivity_analysis_v2.py — 実行ログ

**実行日時:** 2026-02-21
**スクリプト:** `v34.0/mc_sensitivity_analysis_v2.py`
**対応:** v34.0 ng.md 指摘 #1【HIGH】: 実行ログの記録
**修正内容:** v33.0 WARNING #1 対応 — dynamic n_max per sampling range

---

## 実行出力（完全ログ）

```
=================================================================
KSAU v34.0 Section B-1 - MC Sensitivity Analysis v2
FIX: Dynamic n_max per sampling range (v33.0 WARNING #1)
=================================================================
  N_leech    = 196560
  R4         = 21.055899
  r_s (BAO)  = 147.09 Mpc
  THRESH     = 0.00176803805 (Planck_sigma, full precision)
  N_MC       = 100,000
  seed       = 42
  Bonferroni alpha = 0.05/21 = 0.002381

n_max (FIX): computed from midpoint of each range (not fixed at r_s)

Range                     Midpoint   n_max (FIX)   n_max (OLD)
--------------------------------------------------------------
standard [50,500]            275.0            18            12
wide    [30,1000]            515.0            29            12
narrow  [80,300]             190.0            14            12

Range                    RS_MIN   RS_MAX    n_max    hits      MC_p   p<0.05   p<0.0024  Verdict
----------------------------------------------------------------------------------------
standard [50,500]          50.0    500.0       18    2692   0.02692      YES         no  NOT sig (Bonf)
wide    [30,1000]          30.0   1000.0       29    3302   0.03302      YES         no  NOT sig (Bonf)
narrow  [80,300]           80.0    300.0       14    3400   0.03400      YES         no  NOT sig (Bonf)

--- Sensitivity Summary (FIXED n_max) ---
  standard : p = 0.02692
  wide     : p = 0.03302  (delta = +0.00610, +22.7%)
  narrow   : p = 0.03400  (delta = +0.00708, +26.3%)
  Bonferroni threshold = 0.002381

CONCLUSION: All 3 ranges -> NOT significant after Bonferroni.
  Main result is robust to sampling range choice.
  v33.0 WARNING #1 (n_max fix): RESOLVED.
  Main conclusion unchanged: Bonferroni non-significant across all ranges.
=================================================================
```

---

## 結果の解釈

### n_max 修正の効果

| 範囲 | n_max (OLD=固定) | n_max (FIX=動的) | p (OLD) | p (FIX) | 変化率 |
|------|-----------------|-----------------|---------|---------|--------|
| standard [50,500] | 12 | **18** | 0.01176 | **0.02692** | +129% |
| wide [30,1000] | 12 | **29** | 0.00613 | **0.03302** | +439% |
| narrow [80,300] | 12 | **14** | 0.02453 | **0.03400** | +39% |

**解釈:** 動的 n_max 導入により p 値が全体的に上昇した。これは意図通りの修正効果であり：
- wide 範囲では旧 n_max=12 が過度に制約的だったため p が過小評価されていた（v33.0 WARNING #1 の診断通り）
- 修正後は帰無仮説空間が適切に広がり、より保守的な（大きな）p 値が得られた

### 主結論への影響

**全 3 範囲で Bonferroni 補正後 p > α = 0.002381 → 非有意（変化なし）**

v33.0 の報告値（0.01176 / 0.00613 / 0.02453）は n_max バイアスにより過小評価されていたが、主結論（$N_{Leech}^{1/4}/r_s \approx 7$ の統計的有意性なし）は変化しない。

### v33.0 WARNING #1 の最終解消宣言

> **RESOLVED:** `mc_sensitivity_analysis.py` の n_max 固定化問題（v33.0 WARNING #1）は、本スクリプト（v2）の動的 n_max 実装と実行により解消された。

---

*KSAU v34.0 — mc_sensitivity_v2 実行ログ*
*Date: 2026-02-21*
*Status: COMPLETED*
