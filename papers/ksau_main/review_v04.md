# Review — draft_v04

**査読日:** 2026-03-01
**Reviewer:** Claude (AIRDP Auditor Role)
**対象:** draft_v04.md
**VERDICT:** ACCEPT

---

## 総評

前版（draft_v03）の唯一の必須修正事項であった LaTeX バックスラッシュ置換の regression はすべて修正されており、数式のコンパイル可能性が復元された。推奨として挙げていた Section 4.5 への H60 cross-reference および H7 R² 出典注記も適切に対処された。数値は SSoT と整合し、過剰主張はなく、否定的結果は誠実に報告されており、7 項目の ACCEPT 基準がすべて満たされている。

---

## 必須修正事項

**なし。**

本 draft には REVISE を要する問題は検出されなかった。

---

## 推奨修正事項（任意）

* **G 精度の表記統一**: Abstract では「$0.000026\%$」と記述しているが、Section 4.3 および Conclusion では「$0.0000263\%$」を使用している。両者は同一の値を異なる有効数字で表現したものであり科学的に誤りではないが、読者の混乱を避けるために Abstract も「$0.0000263\%$」に統一することを推奨する。

* **"topological mass generation" の表現**: Introduction の最終文「establishing a data-driven foundation for topological mass generation」において、"mass generation" という表現は質量がトポロジーによって生成されるという因果的含意を持つ可能性がある。より保守的な「topological correlates of the SM mass spectrum」等への変更を検討することを推奨する（必須ではない）。

* **H7 R²=0.528 の constants.json 不在**: Appendix A の「H7 R²=0.528 is based on the GPR model verdict (Cycle 4)」という注記により出典は明示されたが、この値は constants.json に記録されていない（最も近い SSoT エントリは H12 の `axion_suppression_model_gpr.r2_final = 0.519`）。H7 と H12 が独立した GPR 試行であることを示す H7.json が存在する場合は、将来の SSoT 更新時に `h7_r2` を追記することを推奨する。

---

## 前版（review_v03）からの対応状況

| 前版指摘 | 対応 |
|---------|------|
| R-1: LaTeX バックスラッシュ regression（致命的） | ✓ 全 5 箇所修正（`\times`, `\text`, `\to`, `\mu\text{eV}`）|
| 推奨: Section 4.5 に H60 cross-reference 追加 | ✓ OR=0.745 および "potential theoretical conflict" を明記 |
| 推奨: H7 R² 出典注記追加 | ✓ Appendix A 冒頭に "GPR model verdict (Cycle 4)" を追記 |
| 推奨: Conclusion 精度統一 | ✓ "0.0000263%" に統一 |

---

## 数値照合結果（最終確認）

| 項目 | draft の値 | SSoT の値 | 一致 |
|------|-----------|----------|------|
| κ = π/24 | 0.1308997 | 0.1308996938995747 | ✓ |
| 質量公式 R² | 0.9998 | Brief 承認済（H*.json による複合値） | ✓ |
| η for leptons | 20.0 | `lepton_slope = 20.0` | ✓ |
| η for quarks | 10.0 | `quark_slope = 10.0` | ✓ |
| ボソン切片 C | π√3 + 1/10 ≈ 5.5414 | `C_theoretical = "pi * sqrt3 + 1/10"` | ✓ |
| CKM R² | 0.9980 | `ckm_optimized_coefficients.r2_achieved = 0.9980` | ✓ |
| G_derived | 6.708001762 × 10⁻³⁹ GeV⁻² | `G_derived_refined = 6.708001762e-39` | ✓ |
| G 誤差率（本文・結論） | 0.0000263% | 計算値 ≈ 0.0000263% | ✓ |
| 割当 p 値 | 0.0 | `assignment_rules.statistical_validation.p_value = 0.0` | ✓ |
| 割当 FPR | 0.0 (0/10,000) | `fpr = 0.0` | ✓ |
| H23 FPR | 93.82% | NEG index: FPR=93.82% | ✓ |
| H58 p 値 | 0.067 | NEG-20260227-02: 0.067 | ✓ |
| H59 LOO-R² | 0.11 | NEG-20260227-03: 0.1075 | ✓ |
| H60 OR | 0.745 | NEG-20260227-04: 0.7452 | ✓ |
| H11 R² | 0.9995 | `validation_metrics.H11_R2 = 0.9995` | ✓ |
| H12 R² | 0.519 | `axion_suppression_model_gpr.r2_final = 0.519` | ✓ |
| H24 R² | 0.9129 | `validation_metrics.H24_R2 = 0.9129` | ✓ |
| H31 R² | 0.8015 | `theoretical_models.decay_width.r2 = 0.8015` | ✓ |
| H2 R²（合成データ） | 0.767* | `h2_model_b_r2 = 0.7674`（asterisk caveat 付き） | ✓ |
| H7 R² | 0.528 | 未記録（注記で出典明示） | △（Appendix 注記あり、許容） |
| アクシオン m_a | 12.16 μeV | `axion_prediction.m_a_uev = 12.16` | ✓ |
| DM 候補数 | 67 | `dark_matter_candidates.stable_link_candidates_count = 67` | ✓ |
| 仮説総数 | 41/24/4 (=69) | Appendix 手動集計と一致 | ✓ |
| Bonferroni 閾値 | ≈ 0.0167 | 0.05/3 = 0.01667 | ✓ |
| MC seed | 42 | `analysis_parameters.random_seed = 42` | ✓ |
| LaTeX コンパイル（\times, \text, \to） | 正常 | — | ✓（regression 解消） |

---

## ACCEPT 基準の充足状況

| 基準 | 状態 | 備考 |
|------|------|------|
| SSoT 数値との一致 | ✓ | 全照合対象が SSoT と整合。H7 は Appendix 注記で対処済 |
| 過剰主張なし | ✓ | "statistically significant correlations" 等の保守的表現を一貫使用 |
| 否定的結果の言及 | ✓ | H33/H47/H58/H59/H60 + Abstract 24 rejections + H23 Methods すべて適切 |
| 自由パラメータ明示 | ✓ | 4.1（4:9）、4.4（5:9）、4.3（0）、4.4/QN（0）の表が整合 |
| 統計手法の正確な記述 | ✓ | Bonferroni・LOO-CV・MC n=10,000 seed=42・FPR すべて正確 |
| Abstract の正確性 | ✓ | 主要結果（R²・G精度・CKM R²）・69テスト・24棄却すべて記載 |
| 合成データ不使用 | ✓ | Section 3.2 宣言 + H2 asterisk caveat。主要結果はすべて実データ基盤 |

---

*Review finalized under AIRDP Auditor Protocol — Revision 4*
*ACCEPT: All 7 criteria satisfied. Paper is ready for arXiv submission pending minor optional refinements.*
