# Researcher Report — Iteration 9

**実施日:** 2026-02-27
**担当タスク:** LOO-CVによる過学習の厳格なチェック、およびボンフェローニ補正閾値との比較

## 1. 実施内容の概要
本タスクでは、仮説 H48（非線形トポロジカル補正 ETD）の最終的な棄却判断を下すため、厳格な統計的監査を実施しました。
具体的には、Iteration 7 で得られた回帰モデルの p 値を、サイクル全体の Bonferroni 補正後閾値（0.05 / 3 = 0.01666）と比較しました。また、Leave-One-Out 交差検証（LOO-CV）を実行し、学習データに対する MAE と未知データ（検証用）に対する MAE を比較することで、モデルの汎化性能と過学習の有無を定量的に評価しました。

## 2. E:\Obsidian\KSAU_Project\cycles\cycle_19
g.md への対応（存在した場合）
存在しませんでした。

## 3. 計算結果
- **観測された p 値:** 0.0435
- **Bonferroni 補正後閾値:** 0.01666
- **有意性判定:** **False** (有意ではない)
- **Training MAE:** 2.2228
- **LOO-CV MAE:** 2.8096
- **MAE 比率 (LOO/Train):** 1.264

統計的検定の結果、観測された p 値 (0.0435) は補正後の有意水準を上回っており、帰無仮説を棄却できません。また、LOO-MAE が学習 MAE に対して約 26% 悪化しており、限られたデータ点（n=9）に対して自由パラメータを追加したことによる汎化性能の限界が示されました。

## 4. SSoT コンプライアンス
- 使用した SSoT 定数のキー: `kappa_theory`, `effective_volume_model`, `particle_data`, `bonferroni_base_alpha`
- ハードコードの混在: なし
- 合成データの使用: なし（実データのみ）

## 5. 修正・作成したファイル一覧
- E:\Obsidian\KSAU_Project\cycles\cycle_19\iterations\iter_09/code/H48_audit.py: LOO-CV および統計監査スクリプト
- E:\Obsidian\KSAU_Project\cycles\cycle_19\iterations\iter_09/results.json: 監査結果データ
- E:\Obsidian\KSAU_Project\cycles\cycle_19\iterations\iter_09/researcher_report.md: 本ファイル

## 6. Reviewer への申し送り
H48 は、非線形項の導入によりベースラインを改善したものの、最終的な統計的有意性基準（Bonferroni 補正後）をクリアすることができませんでした。撤退基準「Bonferroni 補正後 p > 0.016666 → 即座に REJECT」に該当するため、本仮説の追求を正式に終了（REJECT）することを推奨します。
今サイクルで残された課題は、SUCCESS となった H46 の成果の集約と、H47/H48 の「負の発見」の記録となります。
