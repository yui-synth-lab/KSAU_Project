# Researcher Report — Iteration 1

**実施日:** 2026年02月26日
**担当タスク:** PDG崩壊幅データの統合とSSoT拡張

## 1. 実施内容の概要
本イテレーションでは、仮説 H37「Topological Correlates of Decay Width」の検証に向けたデータ基盤の構築を行いました。`ssot/parameters.json` に記録されていた PDG 2024 由来の寿命（$	au$）データを基に、プランク定数 $\hbar$ を用いて崩壊幅 $\Gamma = \hbar / 	au$ を MeV 単位で算出しました。また、算出された崩壊幅を各粒子のトポロジー不変量（交差数 $n$、非結び目化数 $u$、署名 $s$、および行列式 $\ln(\det)$）と統合し、SSoT (`constants.json`) の `particle_data` セクションを拡張して `observed_decay_width_mev` を追加しました。

## 2. E:\Obsidian\KSAU_Project\cycles\cycle_15
g.md への対応（存在した場合）
初回イテレーションのためなし。

## 3. 計算結果
SSoT に定義された全不安定粒子 9 点について、以下の崩壊幅データを統合しました。
- Strange: $5.317 	imes 10^{-14}$ MeV
- Charm: $6.329 	imes 10^{-10}$ MeV
- Bottom: $4.018 	imes 10^{-10}$ MeV
- Top: $1.41 	imes 10^{3}$ MeV (1.41 GeV)
- Muon: $3.000 	imes 10^{-16}$ MeV
- Tau: $2.267 	imes 10^{-9}$ MeV
- W: $2.083 	imes 10^{3}$ MeV (2.08 GeV)
- Z: $2.493 	imes 10^{3}$ MeV (2.49 GeV)
- Higgs: $4.063$ MeV

これらの値は PDG 2024 の実データと整合しており、次イテレーションでの回帰分析の入力として使用可能です。

## 4. SSoT コンプライアンス
- 使用した SSoT 定数のキー: `parameters`, `topology_assignments`, `knot_data`
- ハードコードの混在: なし（$\hbar$ は物理定数として導入）
- 合成データの使用: なし（実データのみ）

## 5. 修正・作成したファイル一覧
- E:\Obsidian\KSAU_Project\cycles\cycle_15\iterations\iter_01\code\integrate_pdg_data.py: 崩壊幅の算出とデータ統合スクリプト
- E:\Obsidian\KSAU_Project\cycles\cycle_15\iterations\iter_01esults.json: 統合されたデータの構造化記録
- E:\Obsidian\KSAU_Project\ssot\constants.json: `observed_decay_width_mev` を追加（SSoT拡張）
- E:\Obsidian\KSAU_Project\cycles\cycle_15\iterations\iter_01esearcher_report.md: 本ファイル

## 6. Reviewer への申し送り
統合された崩壊幅データが `constants.json` に正しく反映されているか、また算出された $\Gamma$ のオーダーが PDG 値と矛盾していないかを確認してください。次イテレーションでは、これらのデータを用いて重回帰分析を実施します。
