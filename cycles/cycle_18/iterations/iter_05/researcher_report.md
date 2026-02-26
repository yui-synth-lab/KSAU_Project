# Researcher Report — Iteration 5

**実施日:** 2026-02-26
**担当タスク:** LOO-CV による過学習チェックと最終モデルの評価（およびタスク4の理論化・統計テストの統合）

## 1. 実施内容の概要
本イテレーションでは、仮説 H45「Linear ST Correction for All Fermions」の最終評価として、トーションによる「体積シフト」としての幾何学的正当性（理論的パラメータ $A$ の制約）を導入した複数モデルを構築し、LOO-CV による過学習チェックと最終的な統計的評価を実施した。
前回の予備分析で示唆された通り、ST 補正が Cycle 17 のベースライン（セクター別切片モデル）を凌駕できるか、また撤退基準（LOO-MAE の劣化）に抵触しないかを検証した。テストした理論パラメータは $A=-0.5$ (TQFT), $A=2.0$ (アキシオンモデル), $A=2.5$ ($\alpha$共通化), および最適化パラメータである。

## 2. E:\Obsidian\KSAU_Project\cycles\cycle_18
g.md への対応
該当なし（前回は CONTINUE 判定）。

## 3. 計算結果
各候補モデルの LOO-CV および全データの R² を算出した結果、以下の知見を得た：

- **ベースライン（Cycle 17）の優位性**: 既存のベースラインモデルは $R^2 = 0.9158$, MAE = 140.5% を誇るが、いかなる ST 補正ユニバーサルモデルもこれを上回ることはできなかった（最適化モデルでも $R^2 = 0.6053$ が限界）。
- **過学習の検知 (LOO-CV)**: 
  - 最適化されたユニバーサルモデル（A=2.8）の Training MAE は 769% であったが、LOO-MAE は 2059% と約2.6倍に跳ね上がり、撤退基準である「LOO-MAE > Training MAE * 1.5」に抵触（過学習）した。
  - 理論制約モデル（A=2.0 や A=2.5）でも LOO-MAE が Training MAE に対して1.5倍以上に劣化している。
- **結論**: $V_{eff}$ に既に含まれる $\ln(det)$ と独立して $A \ln(ST)$ を追加することは、セクター間のギャップを物理的に説明するには不十分であり、かつ統計的な過学習を招くことが証明された。

## 4. SSoT コンプライアンス
- 使用した SSoT 定数のキー: `kappa`, `effective_volume_model`, `particle_data`, `topology_constants`
- ハードコードの混在: なし
- 合成データの使用: なし（SSoT の実データのみを使用）
- SSoT パスの絶対指定: 遵守

## 5. 修正・作成したファイル一覧
- E:\Obsidian\KSAU_Project\cycles\cycle_18\iterations\iter_05/code/st_justification_test.py: 理論モデルの検証および LOO-CV 実装
- E:\Obsidian\KSAU_Project\cycles\cycle_18\iterations\iter_05/results.json: 計算結果・LOO-CV 評価値
- E:\Obsidian\KSAU_Project\cycles\cycle_18\iterations\iter_05/researcher_report.md: 本ファイル

## 6. Reviewer への申し送り
仮説 H45 の対立仮説「$A \ln(ST)$ 項が基底モデルを有意に改善する」は完全に棄却されました。ベースライン（Cycle 17 の $V_{eff}$ + セクター切片）が圧倒的に堅牢であり、これ以上の線形 ST 補正は過学習（LOO-MAE の著しい劣化）を招きます。撤退基準を満たしたため、H45 は REJECT と判定されるべきであると具申します。
