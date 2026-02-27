# Researcher Report — Iteration 5

**実施日:** 2026-02-27
**担当タスク:** ルールに基づいた新規暗黒物質候補の抽出と安定性評価 (H55)

## 1. 実施内容の概要
本イテレーションでは、H55 で定式化された「共鳴安定性ルール ($Det \equiv 0 \pmod{24}$)」に基づき、KnotInfo/LinkInfo 実データ（$n \leq 12$）から新規暗黒物質（DM）候補の抽出を行いました。また、抽出された候補に対し、Topological Stability Index (TSI) を用いた安定性評価を実施しました。

主な発見事項は以下の通りです：
- **結び目の排除**: 数学的に、結び目（1 成分）の行列式は常に奇数であるため、$Det \equiv 0 \pmod{24}$ を満たす結び目は存在しません。これにより、現在のルール下では DM 候補は全て**リンク（2 成分以上）**に限定されることが判明しました。
- **候補の抽出**: $n \leq 12$ の範囲で、581 種のリンクが共鳴安定条件を満たしました。
- **安定性評価**: TSI 閾値（$\geq 24$）を適用した結果、67 種の「極めて安定な」DM 候補が特定されました。

## 2. E:\Obsidian\KSAU_Project\cycles\cycle_22
g.md への対応
本イテレーション開始時、`ng.md` は存在しなかったため、前回の `output_log.md` および `roadmap.md` の指示に従い新規タスクを実行しました。前回の SSoT 準拠（絶対パス排除、実データのみの使用）を継続して徹底しています。

## 3. 計算結果
詳細は `results.json` および `all_candidates.json` を参照。

- **総抽出数**: 581 (All Links)
- **安定候補数 (TSI >= 24)**: 67
- **主要候補例**:
  - **L10a152{1,0}**: $n=10, Det=72, TSI=100.0, V=13.27$. 極めて高い安定性。
  - **L10a155{0,0}**: $n=10, Det=96, TSI=80.0, V=15.48$. Bottom クォーク（$Det=96$）と同じ共鳴次数を持ち、双曲体積 $V$ は Top クォークに近い「重い」DM 候補。
  - **L9a55{0,0,0}**: $n=9, Det=48, TSI=36.0, V=11.75$. 比較的低次の安定状態。

## 4. SSoT コンプライアンス
- 使用した SSoT 定数のキー: `k_resonance`, `topology_assignments`, `dark_matter_candidates.tsi_threshold`
- ハードコードの混在: なし
- 合成データの使用: なし（KnotInfo/LinkInfo 実データのみを使用）

## 5. 修正・作成したファイル一覧
- E:\Obsidian\KSAU_Project\cycles\cycle_22\iterations\iter_05/code/extract_dm_candidates.py: DM 抽出・評価メインスクリプト
- E:\Obsidian\KSAU_Project\cycles\cycle_22\iterations\iter_05/results.json: 抽出結果の要約
- E:\Obsidian\KSAU_Project\cycles\cycle_22\iterations\iter_05/all_candidates.json: 全抽出候補の詳細データ
- E:\Obsidian\KSAU_Project\cycles\cycle_22\iterations\iter_05/researcher_report.md: 本ファイル

## 6. Reviewer への申し送り
結び目が数学的制約（行列式の奇数性）により DM 候補から完全に排除された点は、H55 のルールにおける重要な物理的帰結です。これは、暗黒物質が単一の「結び目」ではなく、複数の位相幾何学的成分が絡み合った「リンク」として存在することを予言しています。抽出された 67 種の安定候補リストが、今後の暗黒物質の相互作用解析や質量スペクトル予測の基盤となります。
