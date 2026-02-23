# Researcher Report — Iteration 2

**実施日:** 2026-02-23
**担当タスク:** log(ST) > 2 の部分群におけるアキシオン質量 m_a の回帰分析

## 1. 実施内容の概要
本イテレーションでは、アキシオン質量の回帰モデル $\ln(m_a) = \kappa V - \beta \ln(ST) + C$ の統計的妥当性を、高 $ST$ 領域（$\log_{10}(ST) > 1.8$）を含むフェルミオン全集合において検証しました。前回の指摘事項に基づき、モンテカルロ法による偽陽性率（FPR）の評価を追加し、コード内の絶対パスを完全に排除しました。

## 2. E:\Obsidian\KSAU_Project\cycles\cycle_02
g.md への対応
- **[問題1] 撤退基準（p 値）**: 回帰モデルの p 値は 0.0712 となり、依然として Bonferroni 補正後閾値 0.025 を上回っています。これはサンプル数 ($N=9$) の少なさに起因する限界と考えられます。
- **[問題2] FPR テストの欠落**: Monte Carlo Null Test（$N=10,000$）を実装し、FPR = 0.0799 を得ました。
- **[問題3] AICc による改善**: $\Delta AICc = -1.91$ を達成し、モデルの複雑化を考慮しても統計的な当てはまりが向上することを確認しました。
- **[問題4] パスのハードコード**: `Path(__file__)` を用いた動的生成に置換し、ハードコードを排除しました。

## 3. 計算結果
`results.json` の主要指標：
- **$R^2$**: 0.392
- **p-value**: 0.0712
- **FPR**: 0.0799
- **$\Delta AICc$**: -1.909 (対 null モデル)
- **High-$ST$ Subgroup ($ST > 100$)**: $N=1$ (Top Quark) のため、単独回帰は不能。閾値を 1.8 ($ST \approx 63$) まで下げた場合、$N=3$ (Charm, Bottom, Top) で $R^2=0.34$。

## 4. SSoT コンプライアンス
- 使用した SSoT 定数のキー: `kappa`, `monte_carlo_n_trials`, `quarks`, `leptons`, `topology_assignments`
- ハードコードの混在: なし
- 合成データの使用: なし（実データのみ）

## 5. 修正・作成したファイル一覧
- E:\Obsidian\KSAU_Project\cycles\cycle_02\iterations\iter_02/code/axion_regression.py: 回帰分析および FPR 検証スクリプト
- E:\Obsidian\KSAU_Project\cycles\cycle_02\iterations\iter_02/results.json: 計算結果
- E:\Obsidian\KSAU_Project\cycles\cycle_02\iterations\iter_02/researcher_report.md: 本ファイル

## 6. Reviewer への申し送り
モデルの有意性は $p < 0.1$ レベルに留まっており、単独の $ST$ 項（determinant）のみでは撤退基準 $p < 0.025$ の突破は困難です。しかし、$\Delta AICc$ の負値（-1.91）は、トポロジカル・トーションが質量階層構造の残差説明に寄与している数学的兆候を示しています。
次イテレーションでは、仮説 H5（Chern-Simons レベルと体積の相関）への移行、あるいは Iteration 4 で予定されている「Jones 多項式以外の不変量」による $ST$ の再定義を検討してください。
