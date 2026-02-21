# Task A: Section 3 Bonferroni n Formal Confirmation

**Date:** 2026-02-21
**Auditor:** Gemini (KSAU Physics Engine & SSoT Auditor)
**Status:** CONFIRMED
**Target:** Section 3 (LSS Coherence / BAO Ratio)

## 1. 調査対象コード

以下のコードを調査し、Section 3 の統計的検定における独立試行数（Bonferroni n）を特定した。

1. `v30.0/code/lss_coherence_check.py`: 初期の比率チェックと候補選定
2. `v30.0/code/factor7_origin_analysis.py`: 最終的なモンテカルロ検定（p値算出）

## 2. 独立検定数 (n) の特定

`v30.0/code/lss_coherence_check.py` において、観測された比率 $BAO / R_{pure}$ に対して以下の 3 つの候補が明示的に比較検討されていることを確認した。

```python
    candidates = {
        "7 (Compact Dim)": 7.0,
        "e^2": np.e**2,  # approx 7.389
        "22/3": 22/3     # approx 7.333
    }
```

これは、研究者が「7（整数）」という結論に至る前に、少なくとも **3つの独立した仮説**（整数性、自然対数の底の二乗、単純分数）を検討したことを示している。したがって、Look-Elsewhere Effect を考慮した Bonferroni 補正を行うための最小の $n$ は 3 である。

さらに、`factor7_origin_analysis.py` の "Part B" では、「整数に近いか」という検定を行っているが、これは上記の候補の中で "7" が最も当てはまりが良かったために選択された事後的な検定（post-hoc test）である。したがって、検定の有意性評価には探索段階の $n=3$ を適用する必要がある。

**結論: $n = 3$**

## 3. Bonferroni 補正後の有意性評価

**Roadmap 引用 p値:**
- Standard MC: $p = 0.032$
- Strict MC: $p = 0.038$

**補正後有意水準 $\alpha_{corr}$:**
$$ \alpha_{corr} = \frac{0.05}{n} = \frac{0.05}{3} \approx 0.0167 $$

**判定:**
- Standard: $0.032 > 0.0167 \implies$ **NOT SIGNIFICANT**
- Strict: $0.038 > 0.0167 \implies$ **NOT SIGNIFICANT**

## 4. 結論

Section 3 (LSS Coherence) の結果は、Bonferroni 補正（n=3）を適用すると統計的有意水準（$\alpha=0.05$）を満たさない。
したがって、ステータスは **MOTIVATED_SIGNIFICANT** から **EXPLORATORY (NOT SIGNIFICANT)** へ変更されるべきである（Roadmap では「MOTIVATED_SIGNIFICANT (格上げなし)」または「EXPLORATORY-SIGNIFICANT (格下げ)」とあるが、有意でないため後者が適切）。

ただし、Roadmap の定義では：
> Bonferroni 補正後有意（p < α）→ MOTIVATED_SIGNIFICANT 維持
> Bonferroni 補正後非有意（p > α）→ EXPLORATORY-SIGNIFICANT へ格下げ

とあるため、**EXPLORATORY-SIGNIFICANT** への格下げが確定した。
