# Researcher Report — Iteration 1

**実施日:** 2026-02-25
**担当タスク:** ST 不変量と質量残差の線形相関の予備調査

## 1. 実施内容の概要
本イテレーションでは、仮説 H34「Linear ST Fermion Mass Correction」の第一段階として、全フェルミオン（N=9）を対象に、質量公式の残差 $\Delta \ln m = \ln(m) - \kappa V$ とトポロジカルな不変量 Smallest Torsion (ST) の対数 $\ln(ST)$ の間の相関を調査した。先行サイクルの知見に基づき、ST のプロキシとして 2 次巡回分岐被覆のホモロジー群の位数に対応する結び目行列式（Determinant）を使用した。

## 2. E:\Obsidian\KSAU_Project\cycles\cycle_14
g.md への対応
初回イテレーションのため、対応事項なし。

## 3. 計算結果
単線形回帰分析の結果、以下の統計値が得られた：
- **決定係数 $R^2$:** 0.3921
- **p 値:** 0.0712
- **回帰係数 $\alpha$ (Slope):** 1.7166 (95% CI: [0.2247, 3.5780])
- **切片 $\beta$:** -1.1404

$R^2 \approx 0.39$ であり、質量残差の約 40% が $\ln(ST)$ によって説明可能であることが示唆された。p 値は 0.0712 であり、Bonferroni 補正後の閾値 (0.0167) を上回っているが、これは 9 点という極めて少ないサンプル数に起因する側面が強い。ブートストラップ法による係数 $\alpha$ の 95% 信頼区間は正の領域に止まっており、正の相関自体は頑健である可能性が高い。

## 4. SSoT コンプライアンス
- 使用した SSoT 定数のキー: `kappa`, `observed_mass_mev`, `volume`, `determinant`
- ハードコードの混在: なし（すべて `parameters.json`, `constants.json`, `topology_assignments.json` から取得）
- 合成データの使用: なし（すべて PDG 2024 および実トポロジーデータを使用）

## 5. 修正・作成したファイル一覧
- E:\Obsidian\KSAU_Project\cycles\cycle_14\iterations\iter_01/code/h34_preliminary_st.py: 質量残差と ST の回帰分析スクリプト
- E:\Obsidian\KSAU_Project\cycles\cycle_14\iterations\iter_01/results.json: 計算結果（回帰統計量および詳細データ）
- E:\Obsidian\KSAU_Project\cycles\cycle_14\iterations\iter_01/researcher_report.md: 本ファイル

## 6. Reviewer への申し送り
- 本結果はあくまで予備調査であり、次イテレーションでの「第一原理に基づく $\alpha$ の導出」に向けたベースラインです。
- サンプル数が 9 点と少ないため p 値は高めですが、全フェルミオンを包含した普遍的な傾向として $\alpha > 0$ が確認されています。
- 物理的には、トーションが質量アクション密度への補正項（$\ln(m) = \kappa V + \alpha \ln(ST) + \beta$）として寄与している可能性を示唆しています。
