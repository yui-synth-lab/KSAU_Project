# Researcher Report — Iteration 4

**実施日:** 2026-02-26
**担当タスク:** Cycle 17 の V_eff を用いたフェルミオン 9 点に対する ln(ST) 線形相関の予備分析

## 1. 実施内容の概要
本イテレーションでは、仮説 H45「Linear ST Correction」の予備分析として、全フェルミオン 9 点の質量予測残差と最小トーション（Smallest Torsion, ST）の間の線形相関を調査した。先行研究に基づき、ST のプロキシとしてトポロジカル行列式（Determinant）を使用し、Cycle 17 で承認された有効体積モデル $V_{eff}$ をベースラインとした。

分析では以下の 2 つのモデルを比較した：
1. **ユニバーサルモデル:** $ln(m) = \kappa V_{eff} + A ln(ST) + B$ （全 9 粒子共通の係数）
2. **セクター別モデル (Baseline):** クォークとレプトンで個別の切片を持つ現行モデル

## 2. E:\Obsidian\KSAU_Project\cycles\cycle_18
g.md への対応
初回イテレーション（H45 としては初）のため、該当なし。
※注: 実際には Iteration 1-3 が H44 に費やされたため、H45 の最初のタスクを本ディレクトリで実施。

## 3. 計算結果
- **ユニバーサル相関:** 質量勾配 $\kappa$ のみを考慮した残差（切片なし）に対し、$ln(ST)$ は有意な相関を示した（$p = 0.0073, R^2_{resid} = 0.6655$）。これは $ln(ST)$ が世代間の質量階層の一部を説明可能であることを示唆する。
- **現行モデルとの比較:** しかし、ユニバーサル ST 補正モデル全体の $R^2$ は **0.6054** であり、セクター別の切片を用いる現行モデル（$R^2 = 0.9158$）には及ばなかった。
- **冗長性の確認:** セクター別の切片を差し引いた後の残差に対しては、$ln(ST)$ は有意な説明力を持たなかった（$p = 0.7627$）。これは、$V_{eff}$ 公式内に既に $ln(det)$ 項（$b = -0.825, \alpha = 2.5$）が含まれているため、ST による線形補正が冗長となっていることを意味する。

## 4. SSoT コンプライアンス
- 使用した SSoT 定数のキー: `kappa`, `effective_volume_model`, `particle_data`, `topology_constants`
- ハードコードの混在: なし
- 合成データの使用: なし（SSoT の実データのみを使用）

## 5. 修正・作成したファイル一覧
- E:\Obsidian\KSAU_Project\cycles\cycle_18\iterations\iter_04\code\st_preliminary_analysis.py: 線形相関分析スクリプト
- E:\Obsidian\KSAU_Project\cycles\cycle_18\iterations\iter_04esults.json: 相関分析結果と統計指標
- E:\Obsidian\KSAU_Project\cycles\cycle_18\iterations\iter_04esearcher_report.md: 本ファイル

## 6. Reviewer への申し送り
$ln(ST)$ は単独では強力な相関（p < 0.01）を示しますが、現行のセクター別切片モデルを凌駕するには至りませんでした。次回のタスクでは、トーションによる「体積シフト」としての幾何学的正当性を定式化し、単なる線形項以上の説明能力（例：非線形項や $\alpha$ の代替）を模索する必要があります。
