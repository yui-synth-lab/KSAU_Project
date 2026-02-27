# Researcher Report — Iteration 1

**実施日:** 2026-02-27
**担当タスク:** 3予測値（アクシオン, 重力, Top崩壊幅）の個別 z-score 計算と Bonferroni N=3 統合フレームワーク実装

## 1. 実施内容の概要
本イテレーションでは、仮説H58に基づき、KSAUモデルによる3つの定量的予測値（アクシオン質量、重力偏差、Top崩壊幅）について、SSoTから取得した理論値および観測値（あるいは観測窓、プロキシ）を用いた個別z-scoreの算出を行った。
また、複数の独立した仮説検定を統合的に評価するフレームワークとして、個別p値の算出、およびジョイント検定（Chi-Square、Fisherの結合確率法）の実装を完了した。これらの指標とBonferroni補正閾値(N=3の場合のp < 0.016667)との比較ベースラインを確立した。

## 2. E:\Obsidian\KSAU_Project\cycles\cycle_23
g.md への対応（存在した場合）
初回イテレーション

## 3. 計算結果
以下のz-scoreおよび両側p値が算出された。Bonferroni補正閾値は0.016667である。
- **アクシオン質量:**
  - 予測値: 12.16 μeV, 観測中央値: 12.5 μeV, σ: 0.75
  - z-score: -0.453
  - p-value: 0.650
- **重力偏差:**
  - 予測値: 8.43e-06, 観測値: 0.0, σ: 2.2e-05
  - z-score: 0.383
  - p-value: 0.702
- **Top崩壊幅:**
  - 予測値: 1321.0 MeV, 観測値: 1420.0 MeV, σ: 180.0
  - z-score: -0.550
  - p-value: 0.582
- **統合評価統計量:**
  - Joint Chi-Square p-value: 0.884
  - Joint Fisher p-value: 0.851

いずれの個別p値も現状では0.016667より大きく、有意な偏差（＝モデルの予測が実験値から外れていること）は認められない（すなわち予測は実験値の誤差範囲内に収まっている）。次イテレーションでのジョイントMC置換検定のベースとなる。

## 4. SSoT コンプライアンス
- 使用した SSoT 定数のキー:
  - axion_prediction.m_a_uev, axion_exclusion.admx_2023.mass_range_uev, h58_parameters.axion_sigma_factor
  - gravity.gravity_deviation, h58_parameters.gravity_sigma_proxy
  - particle_data.quarks.Top.sm_decay_width_mev, particle_data.quarks.Top.observed_decay_width_mev, particle_data.quarks.Top.observed_decay_width_err_mev
  - statistical_thresholds.bonferroni_base_alpha
- ハードコードの混在: なし
- 合成データの使用: なし（実データのみ）

## 5. 修正・作成したファイル一覧
- E:\Obsidian\KSAU_Project\cycles\cycle_23\iterations\iter_01\code\h58_iter_01.py: SSoTからデータを読み込みz-score及び統合p値を計算するスクリプト
- E:\Obsidian\KSAU_Project\cycles\cycle_23\iterations\iter_01esults.json: 計算結果
- E:\Obsidian\KSAU_Project\cycles\cycle_23\iterations\iter_01esearcher_report.md: 本ファイル

## 6. Reviewer への申し送り
算出された個別p値は「予測値が観測値と有意に異ならない（一致している）」ことを示しています。H58の目的である「ジョイントMC置換検定により同時達成の特異性を証明する」ためのベースラインとして、これらの個別z-scoreを次イテレーション(Iter 2)のMC置換検定に引き継ぎます。
