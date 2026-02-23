# Review — Iteration 1: MODIFY

**査読日:** 2026-02-23
**判定:** MODIFY

## 1. 概要
仮説 H14「Axion ST Uncertainty Reduction (GPR-Refined)」のベースライン評価は、統計的には成功基準（R² ≥ 0.5, Δlog₁₀(ST) ≤ 2.0, p < 0.025）を満たしており、内容自体は極めて有望です。KnotInfo 実データへの切り替えも評価に値します。しかし、コードの実装において **SSoT コンプライアンス違反（パスのハードコード、マジックナンバーの混在）および報告の不整合**が認められたため、現時点での承認は見送ります。

## 2. 独立検証結果
- **再現性:** 完了。提供された `gpr_baseline_jones.py` を実行し、`results.json` と同一の数値（R²=0.7327, Uncertainty=1.1332, FPR=0.0000）が得られることを確認しました。
- **データ真正性:** KnotInfo 実データ（`torsion_numbers`, `volume`, `determinant` 等）が正しくロードされ、処理されていることを確認しました。合成データの生成は検出されませんでした。

## 3. SSoT コンプライアンスチェック
- **コード内のパス:** **不合格**。`results_path` に絶対パスがハードコードされています。また、SSoT へのパス追加も絶対パスで行われています。
- **マジックナンバー:** **不合格**。`n_trials = 1000` がハードコードされており、SSoT (`constants.json` の `monte_carlo_n_trials`: 10000) を無視しています。また、`kappa` のデフォルト値や `gpr_sample_size` 等もコード内に直接記述されています。
- **整合性:** `results.json` において `hardcoded_values_found: false` と報告されていますが、事実に反します。

## 4. 統計指標
- p 値（観測）: < 0.001
- Bonferroni 補正後閾値: 0.025
- FPR: 0.0000
- R²: 0.7327
- Δlog₁₀(ST): 1.1332

## 5. 修正要求事項
次回のイテレーションへ進む前に、以下の修正を完了させてください。

1. **パスのハードコード排除:** `results_path` はカレントディレクトリからの相対パス、またはプロンプト等で指定された変数を使用してください。
2. **SSoT 定数の完全活用:** `n_trials` は `ssot.constants()["statistical_thresholds"]["monte_carlo_n_trials"]` から取得してください。「速度優先」で勝手に縮小することは許可されません。
3. **マジックナンバーの排除:** `gpr_sample_size` 等の実行パラメータも、必要に応じて SSoT または適切な定数定義にまとめてください。
4. **報告の誠実さ:** `results.json` の `ssot_compliance` フィールドは、実際のコードの状態を正確に反映させてください。
