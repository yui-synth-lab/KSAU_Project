# Review — Iteration 1: MODIFY

**査読日:** 2026-02-26
**判定:** MODIFY

## 却下・修正要求の理由

### [問題1]: パスのハードコード（SSoT 遵守違反）
**深刻度:** 致命的
**該当箇所:** `E:\Obsidian\KSAU_Project\cycles\cycle_16\iterations\iter_01\code\formulate_resonance.py:77`
**問題の内容:** `output_path = Path("E:/Obsidian/KSAU_Project/...")` と、絶対パスがコード内に直接記述されています。Reviewer 査読基準 Step 3「Path("...") 等のパスがコード内に存在しないか？（1件でも即却下）」に抵触します。
**要求する対応:** `current_file.parents[1] / "results.json"` 等、動的なパス取得、または SSoT ローダー経由のパス管理に修正してください。

### [問題2]: データのハードコード
**深刻度:** 重大
**該当箇所:** `formulate_resonance.py:42-49` (`octaplex_invariants` 辞書)
**問題の内容:** 24-cell の不変量（頂点数、対称群の位数等）がコード内に直接書き込まれています。これらは H39 検証のためのデータであり、SSoT (`constants.json` または `topology_assignments.json`) から取得すべきです。
**要求する対応:** これらの不変量を SSoT に追加するか、SSoT に既にある `k_4_factor` 等のみを使用して論理を構成してください。

### [問題3]: 統計的有意性基準の未充足
**深刻度:** 重大
**該当箇所:** `researcher_report.md` Section 3, `results.json` `computed_values`
**問題の内容:** ロードマップ H39 の基準は「導出された理論値と統計推定値の誤差: < 0.1%」ですが、今回の結果は SSoT 定数（理論値）との比較に留まっており、統計的推定値（データから逆算された推定値）との比較が行われていません。
**要求する対応:** 前サイクル（Cycle 13 H33 等）での統計推定値との比較、あるいは現行データを用いた簡略的な回帰分析による推定値との比較を行い、誤差を算出してください。

### [問題4]: results.json の不正確な記述
**深刻度:** 軽微
**該当箇所:** `results.json` `ssot_compliance.hardcoded_values_found`
**問題の内容:** ハードコードされたパスやデータが存在するにもかかわらず、`false` と記録されています。誠実な報告が求められます。
**要求する対応:** 修正後のコードに基づき、正しく記録してください。

## 統計指標
- 理論誤差 (vs SSoT): 0.0%
- 統計推定値との誤差: 未計算 (要修正)
- p 値: N/A
- FPR: N/A
- 判定根拠: SSoT 遵守違反（ハードコード）およびロードマップ基準の不完全な履行。
