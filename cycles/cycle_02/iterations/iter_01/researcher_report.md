# Researcher Report — Iteration 1

**実施日:** 2026-02-23
**担当タスク:** 既存の fermion 質量公式への ST (Smallest Torsion) 項の導入と残差分析

## 1. 実施内容の概要
本イテレーションでは、`src/ksau_simulator.py` に実装されている既存の fermion 質量公式をベースラインとし、これにトポロジカル・トーション $ST$ (Smallest Torsion) 項を導入することで、予測精度の向上が見られるかを検証しました。
$ST$ のプロキシとして、`axion_suppression_model` の定義（`det_exponent: 2.0`）に基づき、2-fold branched cover の行列式（`determinant`）の対数を使用しました。
全 9 種類のフェルミオン（クォーク 6 種、レプトン 3 種）を対象に、ベースラインモデルの残差と $\ln(ST)$ の相関分析を行い、線形補正を適用しました。

## 2. E:\Obsidian\KSAU_Project\cycles\cycle_02
g.md への対応
初回イテレーションのため、対応事項はありません。

## 3. 計算結果
`results.json` に記録された主要な数値は以下の通りです。

- **Baseline MAE:** 490.41%
- **ST-Corrected MAE:** 363.08%
- **ST Correlation (r):** -0.6487
- **ST p-value:** 0.0588
- **Delta AICc:** +0.1761

$ST$ 項（$\ln(det)$）の導入により、全フェルミオンの MAE は 490% から 363% へと約 26% 改善しました。相関係数 $r = -0.65$ は中程度の負の相関を示していますが、p 値は 0.0588 となり、有意水準 0.05 を僅かに上回りました。また、AICc が僅かに増加（+0.18）したことから、現時点のベースラインに対して $\ln(det)$ を単一の補正項として追加することの統計的正当化は、情報量規準の観点からは不十分であるという結果になりました。

## 4. SSoT コンプライアンス
- 使用した SSoT 定数のキー: `kappa`, `G_catalan`, `quarks`, `leptons`, `topology_assignments`
- ハードコードの混在: なし
- 合成データの使用: なし（実データのみ）
- `SSOT()` クラスを用いてすべてのパスを自動解決しました。

## 5. 修正・作成したファイル一覧
- E:\Obsidian\KSAU_Project\cycles\cycle_02\iterations\iter_01/code/analyze_st.py: 質量公式の残差分析と ST 項の導入検証スクリプト
- E:\Obsidian\KSAU_Project\cycles\cycle_02\iterations\iter_01/results.json: 計算結果の構造化データ
- E:\Obsidian\KSAU_Project\cycles\cycle_02\iterations\iter_01/researcher_report.md: 本ファイル

## 6. Reviewer への申し送り
既存の `ksau_simulator.py` の公式は、現在の `topology_assignments.json` に対しては非常に高い MAE を示しています。これは、以前のサイクルで使用されていたトポロジー割り当て（例: Muon=6_1, Tau=7_1）が変更されたこと、あるいは公式自体のパラメータ（$10\kappa$ 等の係数）の調整が必要であることを示唆しています。
しかし、本タスクの目的である「ST 項の導入」が MAE を改善させる傾向にあることは確認できました。次ステップでは、より広範なトーション不変量（Alexander/A-polynomial 等）を用いた ST の精緻化が期待されます。
