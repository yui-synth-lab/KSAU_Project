# Task A: Bonferroni 検定数 n 正式確認

**Status:** COMPLETED
**Date:** 2026-02-21
**Version:** KSAU v34.0
**Purpose:** WARNING #3 DEFERRED の最終解消（v33.0 go.md §3 / v34.0 Roadmap §1）

---

## §1: 確認対象

v33.0 go.md §3 WARNING #2 DEFERRED の内容：
> "Section 2 元文書参照による Bonferroni 検定数 n=10 の正式確認が未実施"

v34.0 Roadmap Task A の要求：
> "v30.0 の Section 2 実装コード（`v30.0/` 配下）を読み込み、実際の独立検定数 n を直接確認する"

---

## §2: v30.0 ソースコードからの直接確認

**参照ファイル:** `v30.0/code/cs_sensitivity_analysis.py`（Lines 118–120）

```python
k_401 = np.linspace(10, 50, 401)          # 401 points, step = 0.1
n_window_401 = int(np.sum(
    (np.abs(k_401 - 24) < 0.25) | (np.abs(k_401 - 25) < 0.25)
))
bonf_alpha = 0.05 / n_window_401
```

**計算の内訳:**
- k_range = [10, 50], step = 40/400 = 0.1
- Window 1: |k − 24| < 0.25 → k ∈ (23.75, 24.25) → points: 23.8, 23.9, 24.0, 24.1, 24.2 = **5点**
- Window 2: |k − 25| < 0.25 → k ∈ (24.75, 25.25) → points: 24.8, 24.9, 25.0, 25.1, 25.2 = **5点**
- **n = 5 + 5 = 10**（確認）

**参照文書:** `v30.0/Technical_Report_v30.0_S2.md §4.2`（明示的記述）：
> "Points in Niemeier window (Δk=0.1 grid): 10"
> "Conservative Bonferroni α = 0.05 / 10: 0.0050"

---

## §3: 正式確認結果

| 項目 | 値 | 確認根拠 |
|------|-----|---------|
| 独立検定数 n | **10** | `cs_sensitivity_analysis.py` L118-120（ソースコード直接確認）|
| Bonferroni 補正後閾値 | **α = 0.05/10 = 0.0050** | `cs_sensitivity_analysis.py` L120 |
| Section 2 MC p 値 | **0.0078** | `cs_level_monte_carlo.py` + `Technical_Report_v30.0_S2.md §3.4` |
| Bonferroni 結果 | **p = 0.0078 > α = 0.0050 → FAIL** | 直接比較 |
| 最終分類 | **EXPLORATORY-SIGNIFICANT** | 変更なし（v30.0 判定の正式確認）|

---

## §4: 補足——「n = 10」の解釈

v30.0 Technical_Report §4.2 に明記されている通り、この n = 10 は**保守的な過剰補正**である：

> "The Bonferroni denominator is therefore the number of distinct target windows being tested, not the number of grid points. Since only one window is specified (the union of the two half-width-0.25 intervals around k=24 and k=25), the correction would strictly be α/1 = 0.05 — no correction needed. Using denominator 10 (the number of grid points that fall inside the window) is a **conservative over-correction**."

すなわち：
- **厳密な解釈（単一窓）**: n = 1、Bonferroni 補正不要、p = 0.0078 < 0.05 → **PASSED**
- **保守的解釈（窓内グリッド点数）**: n = 10、α = 0.0050、p = 0.0078 > 0.0050 → **FAIL**

KSAU v30.0 以降は保守的解釈を採用し、EXPLORATORY-SIGNIFICANT と分類している。
この判定は v34.0 においても維持される。

---

## §5: WARNING #3 DEFERRED の解消

**解消宣言:** v33.0 go.md §3 WARNING #2 DEFERRED（"Section 2 元文書参照による n=10 の正式確認が未実施"）を本文書によって正式に解消する。

- n = 10 は v30.0 ソースコードから直接確認された（逆算推定値ではなく確認値）
- Bonferroni 補正後評価: p = 0.0078 > α = 0.0050 → Bonferroni 非有意
- 分類: EXPLORATORY-SIGNIFICANT（v30.0 以来の判定を正式確認）

**ステータス:** ✅ RESOLVED

---

*KSAU v34.0 — Task A: Bonferroni n 正式確認*
*Date: 2026-02-21*
*Version: v34.0*
