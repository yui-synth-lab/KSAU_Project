# Researcher Report — Iteration 5

**実施日:** 2026-02-23
**担当タスク:** 不確定性予測の外部データセットによる交差検証 (H14)

## 1. 実施内容の概要
本イテレーションでは、最適化された GPR モデル（Matern 1.5 カーネル）の汎化性能を検証するため、KnotInfo データセットを「交代結び目 (Alternating)」と「非交代結び目 (Non-alternating)」の2つの独立したサブセットに分割し、相互に交差検証を実施した。

1. **データ分割:** 交代結び目 ($N=1846$) と非交代結び目 ($N=1124$) に分類。
2. **Case A (交代→非交代):** 交代結び目で学習し、非交代結び目でテスト。
3. **Case B (非交代→交代):** 非交代結び目で学習し、交代結び目でテスト。

## 2. E:\Obsidian\KSAU_Project\cycles\cycle_07
g.md への対応
前回（iter_04）は承認（go.md）であったため、本タスクはロードマップ通りの進行である。

## 3. 計算結果
- **Case A (Train: Alt, Test: Non-Alt):**
  - $R^2 = 0.6902$
  - $\Delta \log_{10}(ST) = 1.4243$ (成功基準 $\le 2.0$ を達成)
- **Case B (Train: Non-Alt, Test: Alt):**
  - $R^2 = 0.2023$
  - $\Delta \log_{10}(ST) = 1.1637$ (成功基準 $\le 2.0$ を達成)
- **平均不確定性:** 1.2940

## 4. SSoT コンプライアンス
- 使用した SSoT 定数のキー: `mathematical_constants.kappa`, `analysis_parameters`
- ハードコードの混在: なし（パスは `Path(__file__)` からの相対解決を徹底）
- 合成データの使用: なし（KnotInfo の実データのみを使用）

## 5. 修正・作成したファイル一覧
- E:\Obsidian\KSAU_Project\cycles\cycle_07\iterations\iter_05/code/gpr_cross_validation.py: 交代/非交代結び目による交差検証スクリプト
- E:\Obsidian\KSAU_Project\cycles\cycle_07\iterations\iter_05/results.json: 交差検証結果データ
- E:\Obsidian\KSAU_Project\cycles\cycle_07\iterations\iter_05/researcher_report.md: 本報告書

## 6. Reviewer への申し送り
- Case A では $R^2 \approx 0.69$ と高い汎化性能を示した一方で、Case B の $R^2$ が低迷したのは、学習データ（非交代結び目）のサンプルサイズが小さく、交代結び目の多様性を十分にカバーできなかったためと考えられます。
- しかし、両ケースにおいて予測の不確定性 ($\Delta \log_{10}(ST)$) は 1.1〜1.4 桁に抑えられており、アクシオン抑制因子の推定精度を 2 桁以内にするという物理的要件は、トポロジーのクラスを超えて維持されることが実証されました。
