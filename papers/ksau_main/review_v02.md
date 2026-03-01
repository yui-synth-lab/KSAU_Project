# Review — draft_v02

**査読日:** 2026-03-01
**Reviewer:** Claude (AIRDP Auditor Role)
**対象:** draft_v02.md
**VERDICT:** REVISE

---

## 総評

前版（draft_v01）で指摘した 6 件の必須修正はすべて対処され、大幅に改善された。しかし詳細な数値照合の結果、**Section 4.1 の本文と自由パラメータ表の観測量数が矛盾**していること、**Appendix A の H65 仮説名に旧 η_quark 値（10/7）が残存**し本文の記述（10.0）と矛盾すること、および **H2 の検証が合成データに基づいていることが SSoT に記録されているにもかかわらず Appendix に caveat なしで ACCEPTED と記載**されていることが確認された。3 件の修正が完了すれば ACCEPT 水準に達する見込みである。

---

## 必須修正事項

### [R-1]: Section 4.1 — "9 fermions"（本文）と "12 observations"（表）の矛盾
**深刻度:** 重大
**該当箇所:** Section 4.1（Fermion Mass Formula）本文および直後の自由パラメータ表

**問題:**
Section 4.1 の本文は「The regression of **9 fermions** against their assigned topological $V_{eff}$ achieved $R^2 = 0.9998$」と記述しているが、同セクションの自由パラメータ表は以下のように記載している。

| Model | Free Parameters | Observations | Ratio |
|-------|-----------------|--------------|-------|
| Mass Formula | 4 (a, b, c, C) | **12** | 1:3 |

「9 fermions」の回帰であれば観測量は 9 件であり、自由パラメータ 4 件との比率は 4:9（≈0.44）であって 1:3（≈0.33）にならない。「12 observations」であれば本文は「12 SM particles」と記述すべきである。

内訳の候補:
- **9 fermions**: e, μ, τ, u, d, s, c, b, t の 9 粒子（ボソン W/Z/H を除外）
- **12 particles**: 上記 9 フェルミオン + W, Z, H の 3 ボソンを含めた場合

Brief §2 は「フェルミオン質量公式（H1, H11, H35, H41, H65）」と「12粒子トポロジー割当（H49, H55, H64）」を別項目として記載しており、質量公式の適用範囲を明確にする必要がある。SSoT `validation_metrics.H11_R2 = 0.9995` は H11 単体（12 粒子モデル）の値であり、R²=0.9998 の適用範囲と整合させる必要がある。

**修正要求:**
本文の記述と表の観測量数を一致させること。具体的には:
- 回帰対象が 9 フェルミオンであれば: 表の "12" を "9" に修正し、比率を "4:9" に更新すること
- 回帰対象が 12 粒子であれば: 本文の "9 fermions" を "12 SM particles" に修正すること（この場合、ボソンへの適用がセクター別 η の定義外であることを注記すること）

---

### [R-2]: Appendix A — H65 の仮説名に旧値 "クォーク(10/7)" が残存（本文と矛盾）
**深刻度:** 重大
**該当箇所:** Appendix A、H65 の行

**問題:**
Appendix A には以下のように記載されている。

| H65 | **レプトン(20)・クォーク(10/7)係数導出** | 25 | accepted | error<0.04% |

しかし Section 2 では「yielding $\eta = 20.0$ for leptons and $\eta = 10.0$ for quarks」と記述されており、SSoT にも以下のように記録されている。

```json
"theoretical_mass_laws": {
    "quark_slope": 10.0,
    "lepton_slope": 20.0
}
```

`10/7 ≈ 1.429` と `10.0` は全く異なる値であり、同一の論文内で矛盾した数値が並存している。これは KSAU 理論の核心パラメータの不整合であり、外部査読者は「どちらが正しいのか」を判断できない。

また、この矛盾は Brief にも存在する（Brief: "quark=10/7"、SSoT: `quark_slope=10.0`）。Brief と SSoT の間の上位権威は SSoT であるため（CLAUDE.md §2）、SSoT の値（10.0）が権威的である。

**修正要求:**
1. Appendix A の H65 行の名称を実際の確認値に一致させること。SSoT が `quark_slope=10.0` を記録している場合は「クォーク(10.0)係数導出」に更新すること。
2. H65.json の判定結果を確認し、H65 が実際に確立した η_quark の値（10/7 か 10.0 か）を明確にすること。もし H65 の判定が `10/7` であれば、Section 2 と SSoT の修正が必要（Orchestrator 管轄）。もし `10.0` であれば、Appendix の仮説名のみを修正する。
3. 本文（Section 2）と Appendix（H65 名称）で同一の値を使用することを保証すること。

---

### [R-3]: Appendix A — H2 が合成データ検証に基づくが caveat なし
**深刻度:** 重大
**該当箇所:** Section 3.2（本文）、Appendix A H2 行

**問題:**
Appendix A には以下のように記載されている。

| H2 | Axion ST Uncertainty | 1 | **accepted** | R²=0.767 |

しかし SSoT `constants.json` には以下の警告が記録されている。

```json
"model_validation": {
    "_warning": "...ln_ST は合成データ（-κV - det_exponent*ln_det + noise）であり、
    実観測値に対する検証結果は別途記録すること。"
}
```

H2 の R²=0.767 は合成的に生成された `ln_ST` を目的変数とした回帰の結果である。一方、実データによる検証は H12（Axion ST Real Data, R²=0.519, Cycle 6）で別途実施されており、大幅に低い精度を示している。

Section 3.2 には「All primary results are based exclusively on real observational data」と明記されているが、H2 を caveat なしで "accepted" として Appendix に掲載することは、合成データによる検証結果を論文内に含めることになり、この主張と矛盾する。

Brief §2「含めないもの」にも「合成データに基づく結果」が明示されている。

**修正要求:**
以下のいずれかの修正を行うこと。

**選択肢 A（推奨）:** Appendix A の H2 行に脚注または注記を追加する。
```
| H2 | Axion ST Uncertainty | 1 | accepted* | R²=0.767* |
```
*注: R²=0.767 は合成 ln_ST データ（-κV-β·ln(Det)+ε）による検証値。実データ検証は H12 (R²=0.519, Cycle 6) を参照。

**選択肢 B:** Appendix の説明文冒頭に「Appendix A contains all 69 hypotheses as historical records. Note: H2 was initially validated against synthetic ln_ST targets; real-data validation is recorded in H12 (Cycle 6).」を追加する。

合成データ結果を黙示的に "accepted" として論文に含めることは、査読基準 7（合成データ不使用）に違反する。

---

## 推奨修正事項（任意）

* **H7 の R² 値の確認**: Appendix A H7 は "R²=0.528" と記載しているが、SSoT `axion_suppression_model_gpr.r2_final = 0.519`（H12 の実データモデル）と不一致。H7.json の値を確認し、0.528 の出典を明記するか、SSoT 記録値と一致させることを推奨。

* **H64 FPR の表記統一**: Section 4.2 では "FPR = 0.0 (0/10,000 permutations; resolution = 10⁻⁴)" と記述しているが、Appendix A H64 行では "FPR < 0.2%" と記載されている。前版で修正された Section 4.2 の精確な表記と一致させることを推奨: "FPR = 0.0"。

* **H53 の精度表記統一**: Section 4.3 では "0.0000263%" と記述しているが、Appendix H53 では "0.000026%" と記述。有効数字を統一することを推奨。

* **Conclusion の "topological landscape"**: "a robust, transparent, and reproducible map of the topological landscape of particle physics" — "topological landscape of particle physics" は技術的文脈では問題ないが、Brief §7 の「装飾的比喩の排除」の精神からは "topological phase space of the SM spectrum" 等のより技術的な表現が望ましい（軽微）。

---

## 前版（review_v01 Revised）からの対応状況

| 前版指摘 | 対応 |
|---------|------|
| R-1: C = π√3 + 1/10 に修正 | 解消 ✓ |
| R-2: Abstract に "24 documented rejections" 復元 | 解消 ✓ |
| R-3: DM 候補 67 件を Section 4.5 に追加 | 解消 ✓ |
| R-4: アクシオン 12.16 μeV・ADMX 範囲を Section 5.2 に記述 | 解消 ✓ |
| R-5: H23（K=24 のトートロジー）を Methods に追加 | 解消 ✓ |
| R-6: Appendix A を全 69 仮説に拡張 | 解消 ✓ |
| 推奨: grammar "face"→"faces" | 解消 ✓ |
| 推奨: CKM model 記述を "logit-geometric" に修正 | 解消 ✓ |
| 推奨: References に journal 情報追加 | 解消 ✓ |
| 推奨: Section 4.2 FPR を精確な値に更新 | 解消 ✓ |

---

## 数値照合結果

| 項目 | draft の値 | SSoT の値 | 一致 |
|------|-----------|----------|------|
| κ = π/24 近似値 | 0.1308997 | 0.1308996938995747 | ✓ |
| 質量公式 R² | 0.9998 | `H11_R2 = 0.9995`（H11 単体） | △（複合モデルの SSoT 出典なお不明確） |
| η for leptons | 20.0 | `lepton_slope = 20.0` | ✓ |
| η for quarks（本文） | 10.0 | `quark_slope = 10.0` | ✓ |
| η for quarks（Appendix H65 名） | 10/7 | `quark_slope = 10.0` | ✗（R-2） |
| ボソン切片 C | π√3 + 1/10 ≈ 5.5414 | `C_theoretical = "pi * sqrt3 + 1/10"`, C=5.5414 | ✓（前版 R-1 解消） |
| CKM R² | 0.9980 | `ckm_optimized_coefficients.r2_achieved = 0.9980` | ✓ |
| G_derived（精度） | 6.708001762 × 10⁻³⁹ | `G_derived_refined = 6.708001762e-39` | ✓ |
| G 誤差率 | 0.0000263% | 計算値 ≈ 0.0000263% | ✓ |
| 割当 p 値 | 0.0 | `p_value = 0.0` | ✓ |
| 割当 FPR（本文） | 0.0 (0/10,000) | `fpr = 0.0` | ✓ |
| H58 p 値 | 0.067 | NEG-20260227-02: 0.067 | ✓ |
| H59 LOO-R² | 0.11 | NEG-20260227-03: 0.1075 | ✓（有効桁内） |
| H60 OR | 0.745 | NEG-20260227-04: 0.7452 | ✓（有効桁内） |
| H2 R² | 0.767 | `h2_model_b_r2 = 0.7674`（丸め ✓） | △（合成データ起源の警告あり — R-3） |
| H12 R² | 0.519 | `axion_suppression_model_gpr.r2_final = 0.519` | ✓ |
| H11 R² | 0.9995 | `validation_metrics.H11_R2 = 0.9995` | ✓ |
| H24 R² | 0.9129 | `validation_metrics.H24_R2 = 0.9129` | ✓ |
| H31 R² | 0.8015 | `theoretical_models.decay_width.r2 = 0.8015` | ✓ |
| H7 R² | 0.528 | `axion_suppression_model_gpr.r2_final = 0.519`（GPR 最終値） | △（H7.json による確認が必要） |
| アクシオン質量 m_a | 12.16 μeV | `axion_prediction.m_a_uev = 12.16` | ✓ |
| DM 候補数 | 67 | `dark_matter_candidates.stable_link_candidates_count = 67` | ✓ |
| Bonferroni 閾値 | ≈ 0.0167 | 0.05/3 = 0.01667 | ✓ |
| MC seed | 42 | `analysis_parameters.random_seed = 42` | ✓ |
| 仮説総数 | 41 ACCEPT / 24 REJECT / 4 MODIFIED | Brief §4 と一致 | ✓ |

---

## ACCEPT 基準の充足状況

| 基準 | 状態 | 備考 |
|------|------|------|
| SSoT 数値との一致 | △ | H65 名称（10/7 vs 10.0）が不一致（R-2）。H7 R² も確認待ち |
| 過剰主張なし | ✓ | Conclusion の表現は適切。DM caveat も明示 |
| 否定的結果の言及 | ✓ | H33/H47/H58/H59/H60 + Abstract の 24 rejections + H23 Methods いずれも適切 |
| 自由パラメータ明示 | △ | Section 4.1 の観測量数が本文（9）と表（12）で矛盾（R-1） |
| 統計手法の正確な記述 | ✓ | Bonferroni・LOO-CV・MC seed・FPR すべて適切 |
| Abstract の正確性 | ✓ | 24 rejections 復元済み。CKM・G・質量公式の数値は SSoT と整合 |
| 合成データ不使用 | △ | H2 が合成 ln_ST 由来と SSoT が記録しているが Appendix に caveat なし（R-3） |

---

*Review generated under AIRDP Auditor Protocol — Revision 2*
*Remaining blockers: R-1 (9 fermions vs 12 obs), R-2 (H65 η value), R-3 (H2 synthetic data caveat)*
*Next action: Writer resolves R-1 through R-3 and resubmits as draft_v03.*
