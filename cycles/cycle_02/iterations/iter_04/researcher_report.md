# Researcher Report — Iteration 4

**実施日:** 2026-02-23
**担当タスク:** Jones 多項式以外の不変量による ST 補完の検証

## 1. 実施内容の概要
本イテレーションでは、仮説 H4 の精度向上を目指し、従来の $ST$ プロキシである行列式（Determinant）に代わる、あるいはこれを補完するトポロジカル不変量を探索しました。
具体的には、Alexander 多項式（特定の複素根での評価値）、3-Genus、Braid Index、Bridge Index、Crossing Number、Signature 等の複素不変量を用い、フェルミオン質量残差との相関分析およびモンテカルロ・シミュレーション（$N=10,000$）による FPR 検定を実施しました。

## 2. E:\Obsidian\KSAU_Project\cycles\cycle_02
g.md への対応
前回の却下（Iteration 2）で指摘された統計的有意性の欠如（$p > 0.025$）を解決するため、複数の独立したトポロジカル不変量を検証しました。
また、パスのハードコード排除、実データ（KnotInfo/LinkInfo）の完全な SSoT 経由での利用を徹底し、解析の透明性と再現性を確保しました。

## 3. 計算結果
主要な不変量と残差の相関分析結果：
- **Determinant**: $R^2 = 0.392, p = 0.0712$ (FPR = 0.0740)
- **Braid Index**: $R^2 = 0.299, p = 0.1279$
- **Crossing Number**: $R^2 = 0.184, p = 0.2496$
- **Alexander Polynomial (at $e^{2\pi i/3}$)**: $R^2 = 0.174, p = 0.2066$
- **Combined (ln(Det) + |Sig|)**: $R^2 = 0.000, p = 0.9572$

検証した全ての単一・複合不変量において、成功基準（$R^2 \ge 0.75, p \le 0.025$）を満たすものは見つかりませんでした。現状では、行列式（Determinant）が最も高い説明力を持っていますが、統計的に有意な補正項としては不十分であるとの結論に達しました。

## 4. SSoT コンプライアンス
- 使用した SSoT 定数のキー: `kappa`, `topology_assignments`, `parameters`
- ハードコードの混在: なし
- 合成データの使用: なし（実データのみ）

## 5. 修正・作成したファイル一覧
- E:\Obsidian\KSAU_Project\cycles\cycle_02\iterations\iter_04/code/analyze_st_complement.py: 複数不変量の相関検証スクリプト
- E:\Obsidian\KSAU_Project\cycles\cycle_02\iterations\iter_04/results.json: 計算結果の統合データ
- E:\Obsidian\KSAU_Project\cycles\cycle_02\iterations\iter_04/researcher_report.md: 本ファイル

## 6. Reviewer への申し送り
不変量の変更による $ST$ の改善を試みましたが、単一の低次幾何不変量では質量階層の微細構造を説明するのに限界があることが判明しました。
行列式が依然として最良のプロキシであることから、H4 を継続する場合は「複数の不変量の非線形結合」あるいは「より高次の Jones 多項式係数」の導入が必要になると予想されます。
次イテレーションでは、成功基準を満たしている H5（$k-V$ 対応）の最終検証へのリソース集中を推奨します。
