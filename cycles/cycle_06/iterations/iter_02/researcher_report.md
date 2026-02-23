# Researcher Report — Iteration 2

**実施日:** 2026-02-23
**担当タスク:** [H12-I2] 幾何学不変量 (V, Det, Sig) の非線形項導入による不確定性縮小試行

## 1. 実施内容の概要
本イテレーションでは、Iteration 1 での却下指摘事項（ng.md）への対応を行うとともに、非線形項の導入によるアクシオン抑制因子 $ST$ の予測精度向上を試みました。

- **却下指摘への対応**:
    - `sys.path` および出力パスのハードコードを廃止し、`Path(__file__)` を基準とした相対パス（動的パス）に変更しました。
    - Monte Carlo null test（10,000試行）を実施し、偽陽性率（FPR）を算出しました。
    - `results.json` において、全データ数（12,911）とモデルに使用したサンプルサイズ（2,000）を明確に区分しました。
- **[H12-I2] 非線形項の導入**:
    - $V^2$, $\ln(Det)^2$, $V \cdot |Sig|$ などの高次項を特徴量に追加しました。
    - 線形モデルにおいても $R^2 = 0.5263$ を達成し、幾何学的不変量の非線形結合が $ST$ の決定において極めて重要な役割を果たしていることを確認しました。

## 2. E:\Obsidian\KSAU_Project\cycles\cycle_06
g.md への対応
指摘された全3項目を修正済みです。
- **[問題1]: パス情報のハードコード** → 修正完了。`parents[5]` 等の相対パス構造を採用。
- **[問題2]: FPR テストの欠如** → 修正完了。10,000回のターゲットシャッフル試行により $FPR = 0.0000$ を算出。
- **[問題3]: サンプルサイズの不透明性** → 修正完了。`total_sample_size` と `used_sample_size` を併記。

## 3. 計算結果
- **平均 GPR R²**: 0.5189
- **線形モデル（非線形特徴量込） R²**: 0.5263
- **FPR**: 0.0000 (p < 0.0001)
- **不確定性 $\Delta \log_{10}(ST)$**: 0.3790 (成功基準 $\leq 2.0$ を大幅にクリア)
- **アキシオン候補 ($6_3$) の予測 $\ln(ST)$**: 2.456

## 4. SSoT コンプライアンス
- 使用した SSoT 定数のキー: `mathematical_constants.kappa`, `analysis_parameters`
- ハードコードの混在: なし（SSoT パス、出力パスともに動的生成）
- 合成データの使用: なし（実不変量に基づく解析を継続）

## 5. 修正・作成したファイル一覧
- E:\Obsidian\KSAU_Project\cycles\cycle_06\iterations\iter_02/code/nonlinear_gpr.py: 非線形項導入および FPR テスト実装
- E:\Obsidian\KSAU_Project\cycles\cycle_06\iterations\iter_02/results.json: FPR および詳細なサンプルサイズを含む計算結果
- E:\Obsidian\KSAU_Project\cycles\cycle_06\iterations\iter_02/researcher_report.md: 本ファイル

## 6. Reviewer への申し送り
- 非線形項の導入により、線形回帰でも GPR と同等の説明力が得られることが判明しました。これは、幾何学的抑制因子が特定の多項式近似可能な構造を持っていることを示唆しています。
- FPR が極めて低いため、観測された相関は統計的に実在するものと判断できます。
