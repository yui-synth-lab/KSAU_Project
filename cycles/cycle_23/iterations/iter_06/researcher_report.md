# Researcher Report — Iteration 6

**実施日:** 2026-02-27
**担当タスク:** 固定α・固定γ（= -v_borromean = -7.327724753 または理論値）での β 単回帰と LOO-CV 実施（LOO-MAE, LOO-R², 各Leave-Out残差を明示）

## 1. 実施内容の概要
本イテレーションでは、仮説H59に基づき、前イテレーション（Iter 5）で導出した理論的固定値 `α = sqrt(2) * kappa` と、SSoT の理論値 `γ = -v_borromean = -7.327724753` を使用し、9つのフェルミオンに対する質量予測モデル（`ln(m) = kappa * V + α * ln(ST) + γ + β`）を構築しました。
このモデルにおいて唯一の自由パラメータである `β` をOLS推定し、Leave-One-Out 交差検証（LOO-CV）を実施しました。これにより、各フェルミオンを除外した場合の予測残差、および過学習の有無（LOO-MAE, LOO-R²）を評価しました。

## 2. E:\Obsidian\KSAU_Project\cycles\cycle_23
g.md への対応
前回却下されたファイルは存在しません。（前回のレビューは CONTINUE）

## 3. 計算結果
`results.json` に記録された主要な計算結果は以下の通りです。
- **固定パラメータ:**
  - $\kappa = 0.1309$
  - $\alpha = 0.18512$ ($\sqrt{2}\kappa$)
  - $\gamma = -7.3277$ ($-v_{borromean}$)
- **推定された $\beta$ (全体):** 10.8638 (p-value: 1.26e-05)
- **Training Metrics:**
  - $R^2$: 0.2948
  - MAE: 2.8053
- **LOO-CV Metrics:**
  - $LOO-R^2$: 0.1075
  - LOO-MAE: 3.1559
- **各 Leave-Out 残差:**
  - Electron: -4.962
  - Muon: 0.631
  - Tau: 3.516
  - Up: -4.415
  - Down: -3.833
  - Charm: 1.526
  - Strange: -0.992
  - Top: 6.310
  - Bottom: 2.220
- **Validation Checks (過学習チェック等):**
  - LOO-MAE $\le$ 2 $	imes$ Train-MAE: **Pass** (3.156 $\le$ 5.611)
  - p-value < Bonferroni Threshold (0.016667): **Pass** (1.26e-05)
  - $LOO-R^2 \ge Train-R^2 	imes 0.95$: **Fail** (0.1075 < 0.2801)

## 4. SSoT コンプライアンス
- 使用した SSoT 定数のキー:
  - `mathematical_constants.kappa`
  - `topology_constants.v_borromean`
  - `particle_data.quarks`
  - `particle_data.leptons`
  - `topology_assignments`
  - `statistical_thresholds.bonferroni_base_alpha`
- ハードコードの混在: なし
- 合成データの使用: なし（実データのみ）

## 5. 修正・作成したファイル一覧
- E:\Obsidian\KSAU_Project\cycles\cycle_23\iterations\iter_06\code\h59_iter_06.py: LOO-CV と β 単回帰を行うスクリプト
- E:\Obsidian\KSAU_Project\cycles\cycle_23\iterations\iter_06esults.json: 計算結果
- E:\Obsidian\KSAU_Project\cycles\cycle_23\iterations\iter_06esearcher_report.md: 本ファイル

## 6. Reviewer への申し送り
$\alpha$ と $\gamma$ を純粋な幾何学理論値に固定し、唯一のパラメータ $\beta$ を用いて推定した結果、モデルの表現力が大幅に制約され、Training $R^2$ が 0.29 程度に留まりました。また、LOO-CV チェックにおいて、$LOO-R^2$ が閾値（Train $R^2 	imes 0.95$）を下回ったため `r2_check` が Fail となりました。
次イテレーション（Iter 7）のロードマップタスク「$\gamma$ と SSoT v_borromean の 1.5% 乖離の理論的説明（固定値か独立パラメータかを明示）」において、この表現力低下（$R^2$の低迷）についての分析と説明を含めて最終結果レポートを作成する予定です。指示の通り進めてよいかご確認をお願いします。