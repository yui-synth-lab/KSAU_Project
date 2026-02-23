# Researcher Report — Iteration 3

**実施日:** 2026-02-23
**担当タスク:** [H12-I3] 最終モデルの Δlog10(ST) 定量化と感度分析

## 1. 実施内容の概要
本イテレーションでは、仮説 H12 (Axion ST 実データ検証) の最終フェーズとして、GPR モデルの不確定性定量化と感度分析を実施しました。

- **モデルの最終化**: Iteration 2 で有効性が確認された非線形項（$V^2$, $\ln(Det)^2$, $V \cdot \ln(Det)$ 等）を含む 8 つの特徴量を使用し、Matern カーネルを用いた GPR モデルを構築しました。
- **不確定性定量化**: 5 分割交差検証 (5-fold CV) により、対数不確定性 $\Delta \log_{10}(ST)$ を算出しました。結果は 0.3790 であり、成功基準である 2.0 以下を大幅にクリアしました。
- **感度分析**: Permutation Importance を用いて各幾何学不変量の寄与度を評価しました。相互作用項 $V \cdot \ln(Det)$ および $V^2$ が予測において支配的な役割を果たしていることが判明しました。
- **アキシオン予測**: $6_3$ 結び目（アキシオン候補）に対する $\ln(ST)$ の予測値（2.456）と標準偏差（0.887）を算出しました。

## 2. E:\Obsidian\KSAU_Project\cycles\cycle_06
g.md への対応（存在した場合）
Iteration 2 において承認（go.md）を得たため、追加の修正事項はありません。Iteration 1 で指摘されたパスのハードコード廃止、FPR テストの実施、サンプルサイズの明示は本イテレーションでも継続して遵守しています。

## 3. 計算結果
- **平均 R² (GPR)**: 0.5189
- **対数不確定性 $\Delta \log_{10}(ST)$**: 0.3790 (成功基準 $\leq 2.0$)
- **FPR**: 0.0000 (10,000試行)
- **主要な寄与変数**:
    1. `v_ln_det`: 2.135
    2. `vol_sq`: 0.680
    3. `ln_det_sq`: 0.080
- **アキシオン候補予測 $\ln(ST)$**: 2.456 ± 0.887

## 4. SSoT コンプライアンス
- 使用した SSoT 定数のキー: `mathematical_constants.kappa`, `analysis_parameters`
- ハードコードの混在: なし（動的パス取得および SSoT ローダーの使用）
- 合成データの使用: なし（KnotInfo の実測データを使用）

## 5. 修正・作成したファイル一覧
- E:\Obsidian\KSAU_Project\cycles\cycle_06\iterations\iter_03/code/final_st_model.py: 最終モデルと感度分析の実装
- E:\Obsidian\KSAU_Project\cycles\cycle_06\iterations\iter_03/results.json: 定量化データおよび感度分析結果
- E:\Obsidian\KSAU_Project\cycles\cycle_06\iterations\iter_03/researcher_report.md: 本ファイル

## 6. Reviewer への申し送り
- 感度分析の結果、$ST$ (Smallest Torsion) は単純な体積スケーリングよりも、体積と行列式の非線形な相互作用（$V \cdot \ln(Det)$）に強く依存していることが示唆されました。これは TQFT における質量と抑制因子の統一的記述に向けた重要な知見です。
- 成功基準をすべて満たしたため、仮説 H12 は「実データによって支持された」と結論付けられます。
