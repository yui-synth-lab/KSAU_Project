# Researcher Report — Iteration 3

**実施日:** 2026年02月25日
**担当タスク:** PDG 崩壊幅データの SSoT 統合と説明変数 (n, u, |s|) の準備

## 1. 実施内容の概要
本イテレーションでは、仮説 H31（崩壊幅の幾何学的抑制）の検証に向けたデータ統合を実施した。
1. **SSoT 統合**: `parameters.json` から粒子の寿命（$	au$）を、`topology_assignments.json` からトポロジー割り当てを取得。
2. **崩壊幅計算**: 寿命データから崩壊幅 $\Gamma = \hbar / 	au$ および $\ln(\Gamma)$ を算出した。
3. **結び目不変量の抽出**: SSoT ローダー経由で KnotInfo/LinkInfo 実データを読み込み、各粒子のトポロジーに対応する交差数 ($n$), 結び目解消数/リンク解消数 ($u$), 符号 ($|s|$) を抽出した。
4. **統合データセットの作成**: 全 12 粒子（クォーク、レプトン、ゲージボソン、ヒッグス）について、幾何不変量と崩壊幅を紐付けた `integrated_data.csv` を作成した。

## 2. E:\Obsidian\KSAU_Project\cycles\cycle_13
g.md への対応
前回イテレーション (Iter 2) は承認 (CONTINUE) されたため、指摘事項への対応はなし。

## 3. 計算結果
作成された `integrated_data.csv` の統計：
- **総粒子数**: 12
- **不安定粒子 (回帰対象)**: 9 (Strange, Charm, Bottom, Top, Muon, Tau, W, Z, Higgs)
- **安定粒子 (境界条件)**: 3 (Up, Down, Electron) -> $\ln(\Gamma)$ に暫定値 -100.0 を割り当て。
- **データ不備の特定**:
  - 交差数 ($n$) および 符号 ($|s|$) は全 12 粒子で取得成功。
  - **結び目解消数 ($u$)**: $n=11$ のリンク（Strange 以下の 7 粒子）において、KnotInfo にデータが存在せず `NaN` となることを確認。

## 4. SSoT コンプライアンス
- 使用した SSoT 定数のキー: `parameters`, `topology_assignments`
- ハードコードの混在: なし（パスは `Path(__file__)` より動的に解決）
- 合成データの使用: なし（KnotInfo/LinkInfo および PDG の実データのみを使用）

## 5. 修正・作成したファイル一覧
- E:\Obsidian\KSAU_Project\cycles\cycle_13\iterations\iter_03/code/data_integration.py: データ統合スクリプト
- E:\Obsidian\KSAU_Project\cycles\cycle_13\iterations\iter_03/integrated_data.csv: 統合されたデータセット
- E:\Obsidian\KSAU_Project\cycles\cycle_13\iterations\iter_03/results.json: 処理統計とプレビュー
- E:\Obsidian\KSAU_Project\cycles\cycle_13\iterations\iter_03/researcher_report.md: 本ファイル

## 6. Reviewer への申し送り
- **安定粒子の扱い**: 初期方針として、安定粒子は $\ln(\Gamma) = -100.0$ として正則化していますが、回帰分析時にこれらを含めると $R^2$ が過大評価される恐れがあるため、次ステップでは「不安定粒子のみの回帰」と「安定粒子を境界とした制約付き回帰」の比較を検討しています。
- **欠損データ ($u$)**: $n=11$ のリンクについて $u$ (unlinking number) が実データソースに存在しません。H31 の多重回帰において、$u$ を除外するか、あるいは代用変数（determinant 等）を検討する必要があるか、統計的判断を仰ぎたいと考えています。
