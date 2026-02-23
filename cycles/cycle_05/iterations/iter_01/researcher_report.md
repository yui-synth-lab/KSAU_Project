# Researcher Report — Iteration 1

**実施日:** 2026-02-23
**担当タスク:** Smallest Torsion (ST) と Volume V の相関データの抽出と初期回帰分析

## 1. 実施内容の概要
本イテレーションでは、仮説 H9 (Geometric Scaling of Smallest Torsion) の初期検証として、実データ（KnotInfo）から双曲体積 $V$ と最小トーション $ST$ (n=2 巡回分岐被覆) を抽出し、線形回帰分析を行いました。
12,911 個の双曲結び目（3-12交点）を対象に、$\ln(ST) = \alpha V + \beta$ のモデル適合度を検証しました。
SSoT (`ksau_ssot.py`) を介して実データを取得し、合成データは一切使用していません。

## 2. E:\Obsidian\KSAU_Project\cycles\cycle_05
g.md への対応（存在した場合）
初回イテレーションにつき、該当なし。

## 3. 計算結果
- **サンプルサイズ:** 12,911 (双曲結び目)
- **決定係数 ($R^2$):** 0.3561
- **p値:** 0.00e+00 (高度に有意)
- **回帰係数 ($\alpha$):** 0.2129
- **切片 ($\beta$):** 0.9709

初期の線形回帰においては、対立仮説 (H1) の成功基準である $R^2 \ge 0.75$ には届かず、現時点では帰無仮説 (H0: $R^2 < 0.5$) を棄却できていません。

## 4. SSoT コンプライアンス
- 使用した SSoT 定数のキー: `axion_suppression_model`, `mathematical_constants`
- ハードコードの混在: なし
- 合成データの使用: なし（実データのみ）
- SSoT ローダー `SSOT` クラスを通じて全てのデータとパラメータを取得。

## 5. 修正・作成したファイル一覧
- E:\Obsidian\KSAU_Project\cycles\cycle_05\iterations\iter_01/code/task_h9_iter1.py: 抽出・回帰分析のメインスクリプト
- E:\Obsidian\KSAU_Project\cycles\cycle_05\iterations\iter_01/results.json: 計算結果 (R^2, p-value, sample size等)
- E:\Obsidian\KSAU_Project\cycles\cycle_05\iterations\iter_01/researcher_report.md: 本ファイル

## 6. Reviewer への申し送り
線形回帰による $R^2$ は 0.356 と低めですが、これは $V$ と $\ln(ST)$ の関係が単純な線形ではなく、高次の幾何学的不変量や非線形な寄与を含んでいる可能性を示唆しています。次イテレーションでの GPR (Gaussian Process Regression) による非線形スケーリングの検証が重要となります。
また、12,911件という大規模な実データを用いたことで、統計的な有意性（p値）は極めて高い結果となりました。
