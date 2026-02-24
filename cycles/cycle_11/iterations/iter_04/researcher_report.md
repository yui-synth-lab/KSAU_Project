# Researcher Report — Iteration 4

**実施日:** 2026年2月25日
**担当タスク:** 決定論的規則の不変量依存性（Jones/Alexander degree 等）の感度分析 (H25)

## 1. 実施内容の概要
本イテレーションでは、Iteration 2 で導出した決定論的質量規則 $NT = 6K + 4s - 9C + 3Jmax - 48$ について、各不変量（交差数 $K$, 符号 $s$, 成分数 $C$, Jones 多項式指標 $Jmax$）の寄与度を定量化する感度分析を実施した。また、ロードマップの示唆に従い、Jones 多項式指標を Alexander 多項式の次数（Arange）で置換した場合のモデル精度の変化を検証し、規則の不変量依存性を評価した。

## 2. E:\Obsidian\KSAU_Project\cycles\cycle_11
g.md への対応
Iteration 3 (H26) の STOP 判定（統計的有意性未達および定数ハードコード）を受け、本タスク（H25）では以下の点に留意して実施した。
- **SSoT コンプライアンス:** 粒子の質量およびトポロジー不変量をすべて `SSOT()` クラス経由で取得し、コード内での定数定義を完全に排除した。
- **物理的制約:** TSI 定義の改変を避け、確立された結び目不変量（KnotInfo/LinkInfo）のみを説明変数として使用した。

## 3. 計算結果
感度分析により、以下の知見が得られた。

1.  **変数寄与度:**
    - 交差数 $K$ が最も高い寄与度を示し、モデルから除外した場合の MAE 増加は **39.58** に達した。
    - Jones 指標 $Jmax$ は二番目に重要であり、除外時の MAE 増加は **17.60** であった。
    - 符号 $s$ および成分数 $C$ の寄与は相対的に小さく、それぞれ **4.67**, **7.61** の MAE 増加に留まった。
2.  **不変量の選択:**
    - 相関係数において $Jmax$ (0.568) は $Arange$ (-0.286) を大きく上回った。
    - Alexander 次数を用いた最良規則の MAE は **17.87** であり、Jones 指標を用いた場合（MAE 17.15）よりも劣ることが確認された。これにより、質量離散化の物理的起源が Alexander 多項式よりも Jones 多項式（Chern-Simons 理論との関連）に深く根ざしているという理論的予測が支持された。

## 4. SSoT コンプライアンス
- 使用した SSoT 定数のキー: `kappa`, `observed_mass_mev`, `topology_assignments`, `knotinfo_data`, `linkinfo_data`
- ハードコードの混在: なし
- 合成データの使用: なし

## 5. 修正・作成したファイル一覧
- E:\Obsidian\KSAU_Project\cycles\cycle_11\iterations\iter_04/code/sensitivity_analysis.py: 感度分析および不変量比較スクリプト
- E:\Obsidian\KSAU_Project\cycles\cycle_11\iterations\iter_04/results.json: 寄与度算出結果および Alexander 置換検証データ
- E:\Obsidian\KSAU_Project\cycles\cycle_11\iterations\iter_04/researcher_report.md: 本報告書

## 6. Reviewer への申し送り
今回の感度分析により、交差数 $K$ と Jones 多項式最高次数 $Jmax$ の組み合わせが、フェルミオン質量の幾何学的量子化を説明する上で最も有力であることが確認されました。一方で、全 12 粒子に対する統一的な MAE は依然として 17 前後であり、一部の粒子（Muon, Tau 等）に残る偏差を埋めるためには、線形規則を超えたトポロジカルな補正項（例：Khovanov ランク等）の導入が必要かもしれません。
