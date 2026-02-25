# Researcher Report — Iteration 3

**実施日:** 2026年02月25日
**担当タスク:** 全 12 粒子（ボソン含む）へのモデル拡張と Bonferroni 補正下での有意性評価 (SSoT固定版)

## 1. 実施内容の概要
本イテレーションでは、Iteration 2 での却下（MODIFY）を受け、SSoT の整合性修正および規定公式に基づく H28 の再検証を実施しました。
1. **SSoT の完全クリーンアップ:** `ssot/parameters.json` から、前回残存していた安定粒子（Up, Down, Electron）の `1e36` というマジックナンバーを完全に削除しました。
2. **SSoT シードの適用:** `h28_revalidation_fixed.py` において、シード値を `42` に固定するのではなく、SSoT (`constants.json`) の `analysis_parameters.random_seed` から動的に取得するように修正しました。
3. **規定公式による再評価:** ロードマップで規定された公式 $TSI = n \cdot u / |s|$ を用い、全 12 粒子のトポロジー割り当てに対して計算を実行しました。

## 2. E:\Obsidian\KSAU_Project\cycles\cycle_12
g.md への対応
- **問題1 (SSoT マジックナンバー):** `ssot/parameters.json` を直接編集し、`1e36` のエントリを削除しました。これにより、安定粒子は回帰分析の対象から自動的に除外（tau=None として処理）されるようになりました。
- **問題2 (コード内シード):** `consts.analysis_parameters.random_seed` を使用するように修正し、SSoT への完全な準拠を達成しました。

## 3. 計算結果
- **決定係数 ($R^2$):** 0.0000
- **FPR:** 1.0000
- **有意性判定:** 非有意（Significant: False）
- **撤退基準への該当:** **FPR > 50% により即座に REJECT 対象**。
- **分析:** 
  - ロードマップ規定の公式 $TSI = n \cdot u / |s|$ を適用した結果、寿命データを持つ主要な 6 粒子（Strange, Charm, Bottom, Top, Z, Higgs）の `unlinking_number (u)` がすべて `0` であるため、TSI が一律 `0` となりました。
  - 数学的に定義不能な粒子（$s=0$ の Muon, Tau, W）および寿命データのない安定粒子を除外すると、説明変数 TSI が定数（0）となるため、崩壊幅との相関は統計的に成立しません。
  - 以上の結果より、H28 は現行の SSoT 公式定義下では棄却されます。

## 4. SSoT コンプライアンス
- 使用した SSoT 定数のキー: `topology_assignments`, `parameters`, `constants`, `statistical_thresholds`
- ハードコードの混在: なし
- 合成データの使用: なし（実データのみ）

## 5. 修正・作成したファイル一覧
- `ssot/parameters.json`: マジックナンバーの完全排除（Version 3）
- `cycles/cycle_12/iterations/iter_03/code/h28_revalidation_fixed.py`: 修正版検証スクリプト
- `cycles/cycle_12/iterations/iter_03/results.json`: 計算結果
- `cycles/cycle_12/iterations/iter_03/researcher_report.md`: 本ファイル

## 6. Reviewer への申し送り
- 指摘された SSoT の不備を完全に修正しました。
- 規定公式を用いた結果、FPR=1.0 となり、撤退基準に該当しました。これは Cycle 10 で $R^2=0.9129$ を出した際の公式（加算モデル）と SSoT の定義（乗除モデル）が矛盾していることに起因します。ロードマップの「恣意的な変更禁止」を遵守した結果、本仮説は現時点で科学的に棄却されるべき状態にあります。次ステップ（Iter 4 以降）の判断をお願いします。
