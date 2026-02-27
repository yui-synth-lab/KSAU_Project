# Researcher Report — Iteration 3

**実施日:** 2026-02-27
**担当タスク:** 個別 Bonferroni 評価 (N=3, p < 0.016667) と統合レポート作成

## 1. 実施内容の概要
本イテレーションでは、前回の Review (MODIFY) で指摘された「合成データ（一様分布からの乱数）生成の禁止」および「3変数の同時ランダム置換（Joint Permutation）の制約違反」に対応するため、コードを全面的に修正しました。
具体的には、`np.random.uniform` による独立した乱数生成を完全に廃止しました。代わりに KnotInfo / LinkInfo から取得した実データのプール（Volume, Determinant, Crossing Number）を使用し、3つの予測値（Top崩壊幅、アクシオン質量プロキシ、重力偏差プロキシ）すべてを**同一の結び目データ（共通のランダムインデックス）**から同時に算出する真のジョイント・モンテカルロ置換検定を実装・実行しました。

## 2. E:\Obsidian\KSAU_Project\cycles\cycle_23
g.md への対応
前回の MODIFY 指摘（致命的エラー）に対して以下の対応を行いました。
1. **合成データの排除**: `np.random.uniform` によるアクシオンおよび重力のランダム値生成を削除しました。
2. **実データからのプロキシ構築**: KnotInfo の実データを用いて、Volume からアクシオン質量のプロキシ（中央値でスケール）、Determinant から重力偏差のプロキシ（中央値からのズレとしてスケール）を算出するロジックを導入しました。これにより、すべて実データの位相不変量から値が導出されます。
3. **ジョイント置換検定の遵守**: 各MC試行（n=10000）において、共通の単一インデックス `top_indices[i]` を用いて、1つの結び目から3つの値（Top, Axion, Gravity）を同時に算出し、変数の独立性を仮定しない厳密なジョイント検定を実現しました。

## 3. 計算結果
`results.json` に記録されたジョイント置換検定の結果は以下の通りです。
- **KSAUモデルのジョイントChi-Square値:** 0.6548
- **モンテカルロ試行数:** 10000回
- **ランダムモデルがKSAU以上の精度（Chi-Square ≤ 0.6548）を出した回数:** 670回
- **MC ジョイント p 値 (FPR):** 0.067
- **Bonferroni 補正後閾値:** 0.016667 (0.05 / 3)

修正後の厳密なジョイント置換検定では、FPR は 0.067 (6.7%) となりました。これは Bonferroni 補正後閾値の 0.016667 を上回っています（`is_significant: false`）。

## 4. SSoT コンプライアンス
- 使用した SSoT 定数のキー:
  - `axion_prediction`, `axion_exclusion`, `gravity`, `h58_parameters`, `particle_data.quarks.Top`, `statistical_thresholds`, `effective_volume_model`, `physical_constants.alpha_em`
- ハードコードの混在: なし
- 合成データの使用: なし（KnotInfo の実データのみを使用し、`np.random.uniform` を排除）

## 5. 修正・作成したファイル一覧
- E:\Obsidian\KSAU_Project\cycles\cycle_23\iterations\iter_03\code\h58_iter_03.py: 合成データを排除し、共通インデックスによるジョイントMC置換検定を実装したスクリプト
- E:\Obsidian\KSAU_Project\cycles\cycle_23\iterations\iter_03esults.json: 修正版計算結果
- E:\Obsidian\KSAU_Project\cycles\cycle_23\iterations\iter_03esearcher_report.md: 本ファイル

## 6. Reviewer への申し送り
MODIFY指摘に完全に対応し、合成データの排除と同一インデックス共有によるジョイント検定を実装しました。
その結果、FPRは 6.7% (0.067) となり、Bonferroni補正閾値 (0.016667) を超過する結果となりました。撤退基準「Bonferroni 補正後 p > 0.016667 → 即座に REJECT」に該当する可能性があります。
査読による最終判定をお願いいたします。