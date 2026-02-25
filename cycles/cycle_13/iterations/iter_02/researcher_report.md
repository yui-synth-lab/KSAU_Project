# Researcher Report — Iteration 2

**実施日:** 2026年02月25日
**担当タスク:** 既存 SSoT データの抽出と κ 回帰のベースライン構築 (FPR追加・ハードコード修正版)

## 1. 実施内容の概要
本イテレーションでは、Iteration 1 で Reviewer より指摘された 3 つの問題（FPR テストの欠落、パスのハードコード、データのハードコード選択）をすべて修正し、再計算を行った。
- **FPR の算出**: 10,000 回のモンテカルロ置換検定を実装し、統一モデル（Unified Kappa Model）の偽陽性率を算出した。
- **パスの動的解決**: `Path(__file__)` を基準とした相対パス解決に移行し、絶対パスのハードコードを排除した。
- **データの動的取得**: `parameters.json` からクォーク・レプトンのリストを自動取得するように変更した。
- **統計的制約の強化**: 自由度不足（N=2）による不安定な回帰を避けるため、N >= 3 のデータセットのみを回帰対象とした。

## 2. E:\Obsidian\KSAU_Project\cycles\cycle_13
g.md への対応
指摘事項に対して以下の通り対応した：
- **[問題1] FPR テストの欠落**: `calculate_fpr` 関数を実装し、10,000 回の試行で `FPR = 0.0039` を得た。これは撤退基準（FPR < 50%）を十分にクリアしている。
- **[問題2] パスのハードコード**: `results.json` の出力パスを `current_dir.parent / "results.json"` に変更し、絶対パスを削除した。
- **[問題3] データのハードコード選択**: `params.get('quarks', {}).keys()` 等を用いて SSoT から動的に粒子リストを生成するように修正した。

## 3. 計算結果
`results.json` に記録された主要な数値は以下の通り：

| 項目 | 値 | 備考 |
|------|---|---|
| 理論値 $\kappa$ | 0.1309 | $\pi/24$ |
| 統一回帰勾配 | 0.0652 | 補正項なしの状態 |
| 統一回帰 $R^2$ | 0.7626 | p = 0.0046 |
| **FPR (Unified)** | **0.0039** | 10,000 回置換検定 |

FPR が 0.39% と極めて低く、この相関が偶然得られる確率は統計的に極めて低いことが実証された。

## 4. SSoT コンプライアンス
- 使用した SSoT 定数のキー: 
  - `mathematical_constants.kappa`
  - `topology_constants.quark_components`
  - `theoretical_mass_laws.lepton_jump`
- ハードコードの混在: なし（パスおよび粒子リストの動的取得化を完了）
- 合成データの使用: なし（実データのみ）

## 5. 修正・作成したファイル一覧
- E:\Obsidian\KSAU_Project\cycles\cycle_13\iterations\iter_02/code/corrected_baseline_regression.py: 修正済み回帰スクリプト
- E:\Obsidian\KSAU_Project\cycles\cycle_13\iterations\iter_02/results.json: FPR を含む計算結果
- E:\Obsidian\KSAU_Project\cycles\cycle_13\iterations\iter_02/researcher_report.md: 本ファイル

## 6. Reviewer への申し送り
- すべての指摘事項を反映しました。
- レプトンセクターの回帰（Electron を除く Muon, Tau のみの場合）は N=2 となり、統計的に不安定（p=1.0 または定義不可）となるため、結果から除外（null）しました。統一回帰（Unified）には Electron を含む V > 0 の全 8 粒子が含まれています。
- FPR の値が 0.0039 となったことで、H33 の対立仮説の妥当性が強化されました。
