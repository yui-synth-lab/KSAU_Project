# Review — Iteration 10: MODIFY

**査読日:** 2026年02月25日
**判定:** MODIFY

## 却下・修正要求の理由

### [問題1]: マジックナンバーのハードコード（SSoT 違反）
**深刻度:** 致命的
**該当箇所:** `h29_final_eval.py:53-56`, `h29_final_eval.py:64` 等
**問題の内容:** 質量公式および補正項の計算において、`10/7`, `2/9`, `7/3`, `1/6`, `7` といった定数がハードコードされている。これらは SSoT の `dimensions` (bulk_total, bulk_compact, boundary_projection) および `topology_constants` (lepton_components) から取得すべき値である。
**要求する対応:** すべての定数を SSoT (SSOT クラス経由) から取得し、リテラル値を排除すること。

### [問題2]: results.json における虚偽申告
**深刻度:** 重大
**該当箇所:** `results.json["ssot_compliance"]["hardcoded_values_found"]`
**問題の内容:** コード内に多数のマジックナンバーが存在するにもかかわらず、`false` と記録されている。これは科学的誠実さの観点から容認できない。
**要求する対応:** コード修正後、正確に申告すること。

### [問題3]: SSoT 統計閾値の不使用
**深刻度:** 軽微
**該当箇所:** `h29_final_eval.py:114`
**問題の内容:** `n_trials = 10000` がハードコードされている。スクリプト冒頭で `thresh = ssot.statistical_thresholds()` を取得しているにもかかわらず、それを使用していない。
**要求する対応:** `thresh.get("monte_carlo_n_trials", 10000)` を使用すること。

## 統計指標
- p 値（観測）: 0.0588
- Bonferroni 補正後閾値: 0.0167
- FPR: 0.0512
- 判定根拠: 統計的には撤退基準に該当しているが、それを証明する実装コードがプロジェクト規約に準拠していないため。
