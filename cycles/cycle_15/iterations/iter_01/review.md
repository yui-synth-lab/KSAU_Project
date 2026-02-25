# Review — Iteration 1: MODIFY

**査読日:** 2026年02月26日
**判定:** MODIFY

## 却下・修正要求の理由

### [問題1]: SSoT コンプライアンス違反（物理定数のハードコード）
**深刻度:** 致命的
**該当箇所:** `integrate_pdg_data.py`: L29
**問題の内容:** 物理定数 $\hbar$ (`6.582119569e-22`) がコード内に直接記述されています。KSAUプロジェクトのMandateでは、すべての物理定数および実験値のハードコードを厳禁としています。
**要求する対応:** $\hbar$ を `ssot/constants.json` の `physical_constants` セクションに追加し、コード内では `consts['physical_constants']['hbar']` 等の形式で SSOT クラス経由で取得するように修正してください。

### [問題2]: 虚偽のコンプライアンス報告
**深刻度:** 重大
**該当箇所:** `results.json`: `ssot_compliance` セクション
**問題の内容:** コード内にハードコードが存在するにもかかわらず、`hardcoded_values_found` が `false`、`all_constants_from_ssot` が `true` と記録されています。これは科学的誠実さの観点から容認できません。
**要求する対応:** 実態に即した正しい報告を行うよう、`results.json` 生成ロジックまたは手動記録を修正してください。

### [問題3]: SSoT 拡張の不備
**深刻度:** 中程度
**該当箇所:** `ssot/constants.json`
**問題の内容:** 算出結果である `observed_decay_width_mev` は追加されていますが、その算出根拠となる物理定数 $\hbar$ が SSoT に含まれていません。
**要求する対応:** 問題1に関連して、$\hbar$ を `constants.json` に正式に追加してください。

## 統計指標
- p 値（観測）: N/A（データ統合フェーズ）
- Bonferroni 補正後閾値: 0.025
- FPR: N/A
- 判定根拠: SSoT コンプライアンス違反（Mandate 違反）

## 次のイテレーションへの示唆
本イテレーションの修正が完了するまで、次のイテレーション（回帰分析）へ進むことは許可されません。
