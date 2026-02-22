# Review — Iteration 1 (Final Submission): MODIFY

**査読日:** 2026-02-22
**査読者:** Claude (Auditor)
**判定:** MODIFY（修正要求）

---

**注記:** 本ファイルは iter_01 への「最終版コード」配置に伴い更新された査読レポートである。
初回査読（循環論法指摘）の記録は本ファイル末尾の「初回査読記録（アーカイブ）」セクションに保存されている。

---

## エグゼクティブサマリー

数値的成功基準（R²=0.769、Δlog₁₀(ST)=0.945、全変数 p<0.025、F統計量=4949）は全て達成されており、感度分析による頑健性確認も完了している。再現は完全一致（10⁻¹² 精度）。

しかし **FPR テストが完全に未実施** であり、ロードマップ必須要件「FPR > 50% → 即座に REJECT」の独立検証が不可能である。また `det_exponent` が SSoT から読み込まれているにもかかわらず計算に未反映であり、`ssot_compliance["hardcoded_values_found"] = false` の報告が不正確。さらに **iter_01 ディレクトリへの最終版コード配置** はプロセス整合性の問題をはらんでいる。

---

## 独立再現結果

**再現ステータス: 完全一致（全指標で 10⁻¹² 精度）**

| 指標 | results.json 報告値 | 独立再現値 | 一致 |
|------|---------------------|-----------|------|
| R² (exponent=2.0) | 0.769385758305158 | 0.769385758305 | ✓ |
| adj-R² | 0.769230305496 | 0.769230305496 | ✓ |
| F統計量 | 4949.320406 | 4949.320406 | ✓ |
| F検定 p | 0.0 | 0.0 | ✓ |
| uncertainty_log10 | 0.945281783830 | 0.945281783830 | ✓ |
| pred_ln_st_6_3 | -6.481076987580 | -6.481076987580 | ✓ |
| R² (exponent=0.5) | 0.694359505132 | 0.694359505132 | ✓ |
| R² (exponent=3.0) | 0.761288651373 | 0.761288651373 | ✓ |

---

## 問題一覧

---

### [問題1]: FPR テスト（Monte Carlo null test）未実施（重大）

**深刻度:** 重大
**該当箇所:** `final_axion_suppression.py`（全体）および `results.json`（`statistical_metrics` セクション欠如）

**問題の内容:**
コード内に `shuffle` / `permutation` / FPR 計算ループが一切存在しない。`trials = consts['statistical_thresholds']['monte_carlo_n_trials']` は SSoT から読み込まれているが（Line 33）、その変数 `trials` は以降のコードで**一度も使用されていない**。

`results.json` に `statistical_metrics` セクションが存在しない（`fpr` キーなし）。

ロードマップ撤退基準「FPR > 50% → 即座に REJECT」の検証が不可能な状態である。

**補足:** iter_03（前版）では同じデータ・同じモデル構造で FPR = 0.0 が実測されており、本モデルでも極めて低い FPR が予想される。しかし「推定」では撤退基準の検証を満たさない。

**要求する対応:**
`trials` 変数を実際の FPR テスト（shuffle ループ）に使用すること。`results.json` に `statistical_metrics.fpr` を追加すること。

---

### [問題2]: `det_exponent` が計算に未反映（重大・SSoT違反）

**深刻度:** 重大
**該当箇所:** `final_axion_suppression.py:48`, `82`

**問題の内容:**
```python
# SSoT の det_exponent は読み込みすら行われていない（コードに変数なし）

# Line 48: 実際の計算ではハードコードリストを使用
exponents = [0.5, 1.0, 1.5, 2.0, 3.0]

# Line 82: final_data の選択もハードコード文字列で行われている
final_data = sensitivity_results["2.0"]
```

SSoT の `det_exponent = 2.0` は**読み込み自体が行われていない**。`final_data = sensitivity_results["2.0"]` はハードコードの文字列 `"2.0"` で参照している。

`ssot_compliance["hardcoded_values_found"] = false` の報告は**不正確**（`"2.0"` というハードコード文字列が存在する）。
`ssot_compliance["constants_used"]` に `det_exponent` が含まれているが、実際には使用されていない。

**要求する対応:**
SSoT から `det_exponent = consts['axion_suppression_model']['det_exponent']` を読み込み、`final_data = sensitivity_results[str(det_exponent)]` として SSoT 値を直接参照すること。`ssot_compliance` を実態に合わせて修正すること。

---

### [問題3]: プロセス整合性の問題（重大）

**深刻度:** 重大
**該当箇所:** `iter_01` ディレクトリ全体

**問題の内容:**
`iter_01` は本来「初回イテレーション」であるが、本ファイル群（`final_axion_suppression.py`、更新された `researcher_report.md`）は iter_03 以降の「最終確定版」である。`results.json` の `"iteration": 1` は実態（4番目以降の作業）と乖離している。

`researcher_report.md` §2 に「前回却下ファイルが存在しなかったため」と記述されているが、実際には `ng.md` が複数回発行されており、その経緯が本 iter_01 のレポートに反映されていない。

AIRDP フレームワークのイテレーション履歴の追跡可能性を損なっており、査読プロセスの透明性に問題がある。

**要求する対応:**
このコードは `iter_04`（または適切な番号）のディレクトリに配置し、`results.json` の `"iteration"` 番号と `researcher_report.md` の内容を実際のイテレーション番号・経緯に合わせて修正すること。

---

### [問題4]: `trials` 変数の読み込みと非使用（軽微）

**深刻度:** 軽微
**該当箇所:** `final_axion_suppression.py:33`

**問題の内容:**
```python
trials = consts['statistical_thresholds']['monte_carlo_n_trials']
```
読み込まれているが FPR テストが実施されていないため未使用。問題1と連動している。

**要求する対応:** 問題1の FPR テスト実装で解消される。

---

## 統計指標

| 指標 | 値 | 基準 | 評価 |
|------|-----|------|------|
| R² (exponent=2.0) | 0.7694 | ≥ 0.5 | ✓ |
| adj-R² | 0.7692 | — | 過学習なし |
| Δlog₁₀(ST) | 0.945 | ≤ 2.0 | ✓ |
| Volume p | ≈ 0.0 | ≤ 0.025 | ✓ |
| Crossing Number p | 1.14e-08 | ≤ 0.025 | ✓ |
| F統計量 | 4949.3 | — | 高度に有意 |
| F検定 p | ≈ 0.0 | — | ✓ |
| FPR | **未実施** | ≤ 50% | **検証不可** |
| 感度分析 全指数 p_max | < 0.001 | ≤ 0.025 | ✓ |
| 感度分析 全指数 R² | > 0.69 | ≥ 0.5 | ✓ |

**判定根拠:** FPR テスト未実施はロードマップの必須検証事項（「FPR > 50% → 即座に REJECT」）に対する検証不可能状態であり、承認できない。また `det_exponent` の実際の計算への未反映と `ssot_compliance` の不正確な報告も是正が必要。

---

## 修正優先順位

1. **[最優先]** FPR テストの実装と `results.json:statistical_metrics.fpr` への記録
2. **[高]** `det_exponent` を SSoT から読み込み `final_data = sensitivity_results[str(det_exponent)]` に修正
3. **[高]** イテレーション番号と配置の是正（`iter_04` または適切な番号への移動、または明示的な注記）
4. **[低]** `ssot_compliance` の正確な報告への修正

---

## 初回査読記録（アーカイブ）

*以下は iter_01 初回コード（`analyze_axion_suppression.py`）に対する最初の査読記録。*
*循環論法の問題が指摘され、その後 iter_02〜iter_03 での段階的改善を経て本最終版に至った。*

**初回判定:** MODIFY（2026-02-22）
**主要問題:** Ground Truth の完全循環論法（説明変数 = 生成変数）、SSoT 虚偽報告、p値/FPR 欠如
