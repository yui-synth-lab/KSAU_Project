# Researcher Report — Iteration 2

**実施日:** 2026年02月26日
**担当タスク:** 交差数・非結び目化数・署名を用いた重回帰分析

## 1. 実施内容の概要
本イテレーションでは、仮説 H37「Topological Correlates of Decay Width」に基づき、崩壊幅 $\ln(\Gamma)$ を目的変数、交差数 $n$、非結び目化数 $u$、および署名の絶対値 $|s|$ を説明変数とする重回帰分析を実施しました。データは Iteration 1 で統合された 9 つの不安定粒子（Strange, Charm, Bottom, Top, Muon, Tau, W, Z, Higgs）を使用しました。

## 2. E:\Obsidian\KSAU_Project\cycles\cycle_15
g.md への対応（存在した場合）
前回の指摘内容（$\hbar$ のハードコードおよび報告の不備）に対し、以下の対応を完了しました。
- **SSoT 拡張:** `ssot/constants.json` の `physical_constants` に `h_bar_mev_s` ($6.582119569 	imes 10^{-22}$) を追加。
- **コード修正:** `iter_01/code/integrate_pdg_data.py` を修正し、定数を SSoT から読み込むように変更。
- **報告の修正:** コンプライアンスチェックを正確に行い、ハードコードが排除されたことを確認。
- **データの再生成:** 修正後のスクリプトを実行し、正当な `iter_01/results.json` を生成しました。

## 3. 計算結果
OLS 重回帰分析の結果、以下の指標が得られました。
- **決定係数 $R^2$:** 0.6132
- **自由度調整済み決定係数 $Adj. R^2$:** 0.3812
- **F-statistic p-value:** 0.1610
- **偏回帰係数:**
  - $n$ (Crossing Number): 7.920 ($p=0.455$)
  - $u$ (Unknotting Number): 11.241 ($p=0.859$)
  - $|s|$ (Signature): -6.379 ($p=0.110$)
  - Intercept: -78.664 ($p=0.499$)

サンプルサイズが小さいため ($N=9$)、個別の変数の p 値は有意水準を下回っていませんが、署名 $|s|$ が最も強い負の相関（安定化への寄与）を示唆しています。

## 4. SSoT コンプライアンス
- 使用した SSoT 定数のキー: `constants.json` (via `iter_01` 経由)
- ハードコードの混在: なし
- 合成データの使用: なし（実データのみ）

## 5. 修正・作成したファイル一覧
- E:\Obsidian\KSAU_Project\ssot\constants.json: `h_bar_mev_s` の追加
- E:\Obsidian\KSAU_Project\cycles\cycle_15\iterations\iter_01\code\integrate_pdg_data.py: 指摘に基づく修正
- E:\Obsidian\KSAU_Project\cycles\cycle_15\iterations\iter_02\code\decay_regression.py: 重回帰分析スクリプト
- E:\Obsidian\KSAU_Project\cycles\cycle_15\iterations\iter_02esults.json: 回帰分析結果
- E:\Obsidian\KSAU_Project\cycles\cycle_15\iterations\iter_02esearcher_report.md: 本ファイル

## 6. Reviewer への申し送り
Iteration 1 の指摘事項をすべて解消した上で、Task 2 を完了しました。回帰分析の p 値は現時点では 0.16 ですが、次イテレーションのモンテカルロ置換検定（FPR）によって、この相関が偶然得られる確率をより厳密に評価します。
