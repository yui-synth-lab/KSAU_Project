# get_observed_s8_z() Methodology: S₈(z) 比較の正当性

**Status:** DRAFT | v22.0 Section 1/2 Supporting Document
**Date:** 2026-02-18
**Author:** Gemini (Simulation Kernel)

---

## 1. 概要 (Abstract)

KSAU フレームワークにおいて、宇宙網の成長抑制（σ₈ テンション）を検証する際、観測データとの比較方法を厳密に定義する必要がある。本文書では、`get_observed_s8_z()` 関数が実施している「報告された S₈(0) からの S₈(z) 復元」の論理的根拠と、その限界について記述する。

## 2. 背景 (Background)

DES Y3, HSC Y3, KiDS-Legacy などの弱重力レンズサーベイは、典型的には有効赤方偏移 $z_{\text{eff}}$ での剪断パワースペクトルを測定している。しかし、宇宙論パラメータの報告値として一般的である $S_8 = \sigma_8 \sqrt{\Omega_m / 0.3}$ は、測定された $S_8(z_{\text{eff}})$ を **$\Lambda$CDM モデルを前提として** $z=0$ に外挿した値である。

KSAU モデルは $\Lambda$CDM とは異なる成長指数 $\gamma$ または成長因子 $D(z)$ を持つため、観測された $S_8(0)$ と KSAU が予測する $S_8(0)$ を直接比較することは、成長過程の差異を無視することになり、物理的に不正確である。

## 3. 方法論 (Methodology)

KSAU の予測値 $S_{8, \text{KSAU}}(z)$ と観測データを整合的に比較するために、以下の手順を採用する：

### 3.1 観測値の復元

サーベイから報告された $S_{8, \text{obs}}(0)$ は、以下の仮定のもとに算出されている：
$$S_{8, \text{obs}}(0) = S_{8, \text{obs}}(z_{\text{eff}}) \cdot \frac{D_{\Lambda\text{CDM}}(0)}{D_{\Lambda\text{CDM}}(z_{\text{eff}})}$$

ここで $D_{\Lambda\text{CDM}}(z)$ は $\gamma = 0.55$ を用いた線形成長因子である。
KSAU の検証コードでは、これを逆算して、実際の観測値に相当する $S_{8, \text{obs}}(z_{\text{eff}})$ を復元する：
$$S_{8, \text{obs}}(z_{\text{eff}}) = S_{8, \text{obs}}(0) \cdot \frac{D_{\Lambda\text{CDM}}(z_{\text{eff}})}{D_{\Lambda\text{CDM}}(0)}$$

これが `get_observed_s8_z()` の実装内容である。

### 3.2 KSAU 予測値との比較

次に、KSAU モデル固有の成長因子 $D_{\text{KSAU}}(z)$ を用いて計算された $S_{8, \text{KSAU}}(z_{\text{eff}})$ を、復元された観測値 $S_{8, \text{obs}}(z_{\text{eff}})$ と比較する。

$$ \chi^2 = \sum \frac{(S_{8, \text{KSAU}}(z_{\text{eff}}) - S_{8, \text{obs}}(z_{\text{eff}}))^2}{\sigma_{S_8}^2} $$

## 4. 正当性と限界 (Justification & Limitations)

### 4.1 正当性 (Justification)

1. **モデル依存性の最小化**: $z_{\text{eff}}$ における実測値に近い状態で比較を行うことで、$\Lambda$CDM による外挿の不確実性を排除できる。
2. **成長指数の検証**: KSAU の特徴である「成長の抑制」が、赤方偏移に応じた変化として正しく捉えられているかを検証可能にする。

### 4.2 限界 (Limitations)

1. **$z_{\text{eff}}$ の精度**: サーベイが報告する $z_{\text{eff}}$ はサンプルの平均的な赤方偏移であり、感度のピークとは必ずしも一致しない。
2. **$\Omega_m$ 依存性**: 復元に使用する $\Omega_m$ がサーベイの最適化値と異なる場合、微小な誤差を生じる可能性がある。

## 5. 結論 (Conclusion)

`get_observed_s8_z()` を通じた比較は、KSAU のような非標準的な宇宙網成長モデルを検証するための、最も公平で保守的なアプローチである。今後の $z=0$ 統一比較への移行に際しても、この復元プロセスは KSAU の予測値を $\Lambda$CDM を介して外挿するための基準点として機能する。
