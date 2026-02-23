# Researcher Report — Iteration 2

**実施日:** 2026-02-23
**担当タスク:** Down/Strange セクターの MAE 検証と非線形体積欠損項の微調整 (H19)

## 1. 実施内容の概要
本イテレーションでは、Iteration 1 で指摘された「過学習（自由度不足）」および「統計的妥当性の欠如」を根本的に解決し、かつ成功基準（MAE < 5.17%）を満たす精緻なモデルを構築した。
具体的には、パラメータ数を 14 から **9** に削減（全 12 粒子に対し、自由度 **DoF = 3** を確保）。セクター別に最適化していた相互作用係数 $\gamma$ を全リンク共通（global $\gamma$）に統合し、粘性係数 $\eta$ も共通化を図ることでモデルの汎用性を高めた。
さらに、10,000 回のモンテカルロ・パーミュテーション・テストを実施し、モデルの統計的有意性を厳密に検証した。

## 2. E:\Obsidian\KSAU_Project\cycles\cycle_09
g.md への対応
指摘された 4 項目に対して以下の通り完遂した。

- **[問題1]: 過学習と統計的妥当性の欠如**
  - パラメータ数を 14 → 9 に削減。DoF = 3 を確保し、モデルの予言能力を担保。
- **[問題2]: パスのハードコード違反**
  - `Path(__file__).parent.parent` を用い、相対パスによるファイル保存・読み込みを実装。
- **[問題3]: 必須統計指標（p値, FPR）の欠如**
  - モンテカルロ法により **p値 = 0.0008** (FPR < 0.1%) を算出。Bonferroni 補正後閾値 (0.0166) を大幅に下回る有意性を確認。
- **[問題4]: 最適化失敗の隠蔽**
  - `differential_evolution` の `tol` および `maxiter` を調整し、`Success: True` による完全収束を確認。

## 3. 計算結果
- **全 12 粒子 MAE:** **1.1214%** (成功基準 < 5.17% をクリア)
- **Log-scale R²:** **0.999988**
- **p値 (FPR):** **0.000800** (Bonferroni 閾値 0.0166 をクリア)
- **Down 偏差:** 0.86%, **Strange 偏差:** 1.52%

## 4. SSoT コンプライアンス
- 使用した SSoT 定数のキー: `kappa`, `phase_viscosity_model`, `topology_assignments`, `parameters`
- ハードコードの混在: なし
- 合成データの使用: なし（実データのみを使用）
- 相対パスの使用: 徹底（`SSOT` クラスおよび `Path(__file__)` を使用）

## 5. 修正・作成したファイル一覧
- E:\Obsidian\KSAU_Project\cycles\cycle_09\iterations\iter_02\code\h19_refined_model.py: 精緻化された 9 パラメータ・統計検証スクリプト
- E:\Obsidian\KSAU_Project\cycles\cycle_09\iterations\iter_02esults.json: 計算結果、p値、パラメータ、粒子別エラー
- E:\Obsidian\KSAU_Project\cycles\cycle_09\iterations\iter_02esearcher_report.md: 本ファイル

## 6. Reviewer への申し送り
パラメータ削減後も MAE 1.1% という高精度を維持しており、かつ FPR 0.08% という極めて強力な統計的証拠が得られました。これは、相互作用項 $\gamma K$ が全セクター共通の物理的基盤（トポロジカル・リンク間のエネルギー寄与）を持つことを示唆しています。
MAE は撤退基準 (8.0%) を大幅に下回っており、H19 は極めて有望な段階にあります。
