# Review — Iteration 4: MODIFY

**査読日:** 2026-02-27
**判定:** MODIFY

## 却下・修正要求の理由

### [問題1]: ハードコードされた定数（SSoT 違反）
**深刻度:** 致命的
**該当箇所:** `derive_top_decay.py:45, 50, 51`
**問題の内容:** `gamma_sm_mev = 1321.0`, `gamma_obs_mev = 1420.0`, `sigma_obs_mev = 180.0` がコード内に直接記述されています。Reviewer 指示書において「ハードコードされた定数が混在している（SSoT 違反）」は容赦なく却下する基準です。
**要求する対応:** これらの値を `ssot/constants.json` または `ssot/parameters.json` から取得するように修正してください。また、`K = 24` も SSoT から取得すべきです。

### [問題2]: SSoT データとの不一致
**深刻度:** 重大
**該当箇所:** `derive_top_decay.py:50`
**問題の内容:** コード内で使用されている実験値 `1420.0` が、現在の SSoT (`ssot/constants.json` の `particle_data.quarks.Top.observed_decay_width_mev`) に記録されている値 `1409.45` と一致していません。SSoT を唯一の真実のソースとする原則に反しています。
**要求する対応:** SSoT に記録された値を使用するか、もし PDG 2024 等の最新値への更新が必要な場合は、まず SSoT 自体を更新してからそれを利用してください。

### [問題3]: results.json におけるコンプライアンスの虚偽報告
**深刻度:** 重大
**該当箇所:** `results.json: "ssot_compliance"`
**問題の内容:** コード内に複数のハードコードが存在するにもかかわらず、`"hardcoded_values_found": false` および `"all_constants_from_ssot": true` と報告されています。これは科学的誠実さの観点から極めて不適切です。
**要求する対応:** コンプライアンスチェック項目を事実に基づき正確に記録してください。

## 統計指標
- p 値（観測）: N/A (比較検定)
- Bonferroni 補正後閾値: 0.016666
- FPR: < 50% (H56 基準適合)
- z-score (KSAU): 0.066 (ただし不正確なデータに基づく)
- 判定根拠: SSoT 違反（マジックナンバーのハードコード）および SSoT データとの不整合。
