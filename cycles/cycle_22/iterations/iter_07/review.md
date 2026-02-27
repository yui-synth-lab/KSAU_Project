# Review — Iteration 7: MODIFY

**査読日:** 2026-02-27
**判定:** MODIFY

## 却下・修正要求の理由

### [問題1]: ハードコードされた定数の継続（SSoT 違反）
**深刻度:** 致命的
**該当箇所:** `stat_validation.py:31, 32`
**問題の内容:** 標準模型の予測値 (`gamma_sm = 1321.0`) および実験不確かさ (`gamma_exp_err = 180.0`) が依然としてコード内に直接記述されています。Iteration 06 の査読において「これらの値はすべて SSoT から取得するように修正してください」と明確に指示されました。SSoT に存在しないのであれば、まず SSoT (`constants.json` 等) に追加した上でコードから参照すべきであり、暫定的に変数として保持することは「マジックナンバーの排除」という原則に反します。

### [問題2]: results.json における不正確なコンプライアンス報告
**深刻度:** 重大
**該当箇所:** `results.json: "ssot_compliance"`
**問題の内容:** `stat_validation.py` 内にハードコードされたマジックナンバーが存在し、報告書でもそれを認めているにもかかわらず、`results.json` では `"hardcoded_values_found": false` および `"all_constants_from_ssot": true` と記録されています。これは Step 3 の「正直に記録されているか？」という基準に照らして不合格です。

### [問題3]: イテレーション割り当ての不整合
**深刻度:** 軽微
**該当箇所:** `roadmap.md` および `output_log.md`
**問題の内容:** 本作業は Iteration 06 の修正作業（Re-validation）ですが、`output_log.md` では Iteration 07 として報告されています。ロードマップ上、Iteration 07 は H57 タスクに割り当てられており、現在の状態では H57 のスロットを消費してしまっています。修正作業は元のイテレーション番号（Iteration 06 Revision 等）で行うか、イテレーション消費を明記すべきです。

## 統計指標
- z-score (KSAU): 0.0077 (SSoT 実験値 1409.45 MeV に対して)
- p 値 (vs KSAU): 0.0443
- Bonferroni 補正後閾値: 0.016666 (N=3)
- 判定根拠: SSoT 違反の継続および報告の不一致。

## 修正要求
1. `gamma_sm` および `gamma_exp_err` を `ssot/constants.json` または `ssot/parameters.json` に適切に追加してください。
2. 追加した定数を `SSOT` クラス経由で取得するようにコードを修正してください。
3. `results.json` のコンプライアンスフィールドを事実に基づき正確に（全ての定数が SSoT 経由であれば `true/false` を適切に）更新してください。
4. 本作業を Iteration 06 の完遂として整理してください（Iteration 07 は H57 のために空けておく必要があります）。
