# Researcher Report — Iteration 1

**実施日:** 2026-02-23
**担当タスク:** GPR モデルのベースライン評価と Jones 不変量の再検証

## 1. 実施内容の概要
本イテレーションでは、仮説 H14「Axion ST Uncertainty Reduction (GPR-Refined)」のベースライン評価を実施した。具体的には、KnotInfo 実データ（交点数 3-12）から、双曲体積 ($V$)、結び目行列式 ($	ext{Det}$)、符号数 ($	ext{Signature}$)、および Jones 多項式を $t = e^{2\pi i / 5}$ で評価した値 ($J(e^{2\pi i / 5})$) を特徴量として抽出した。ターゲット変数 $ST$ (Smallest Torsion) は、2次分岐被覆のねじれ群の最小成分として `torsion_numbers` から導出した。ガウス過程回帰 (GPR) モデル（Matern カーネル + WhiteKernel）を用いて $y = \log_{10}(ST)$ の予測精度と不確定性を評価した。

## 2. E:\Obsidian\KSAU_Project\cycles\cycle_07
g.md への対応
初回イテレーションのため、対応事項なし。

## 3. 計算結果
- **総サンプル数:** 2970 (交点数 3-12)
- **GPR R²:** 0.7327 (成功基準 R² ≥ 0.5 を達成)
- **線形モデル R²:** 0.5098
- **平均不確定性 $\Delta \log_{10}(ST)$ (95% 予測区間幅):** 1.1332 (成功基準 ≤ 2.0 を達成)
- **FPR (偽発見率):** 0.0000 (Monte Carlo 1,000回試行、成功基準 ≤ 0.025 を達成)

## 4. SSoT コンプライアンス
- 使用した SSoT 定数のキー: `mathematical_constants.kappa`, `analysis_parameters`, `axion_suppression_model_gpr`, `statistical_thresholds`
- ハードコードの混在: なし
- 合成データの使用: なし（実データ `KnotInfo` のみを使用）

## 5. 修正・作成したファイル一覧
- E:\Obsidian\KSAU_Project\cycles\cycle_07\iterations\iter_01/code/gpr_baseline_jones.py: GPR モデルの学習、評価、Monte Carlo 検定を行うスクリプト。
- E:\Obsidian\KSAU_Project\cycles\cycle_07\iterations\iter_01/results.json: 計算結果（R², 不確定性, FPR等）を格納。
- E:\Obsidian\KSAU_Project\cycles\cycle_07\iterations\iter_01/researcher_report.md: 本報告書。

## 6. Reviewer への申し送り
- Jones 不変量を複素平面上の特定の点 ($e^{2\pi i / 5}$) で評価した値を特徴量に含めることで、線形モデルよりも高い予測精度が得られている。
- GPR の 95% 予測区間幅は平均して 1.13 桁であり、アクシオン抑制因子の不確定性を 2 桁以内に収めるという物理的要件を十分に満たしている。
- 次のイテレーションでは、非線形カーネルの最適化により、さらなる不確定性の縮小を試みる。
