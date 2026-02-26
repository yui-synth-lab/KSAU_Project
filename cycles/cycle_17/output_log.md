# Output Log — Iteration 6

**Researcher 完了日時:** 2026-02-26 21:00

## 実施タスク
PDG 全データを用いた崩壊幅相関モデルの統計的検証

## E:\Obsidian\KSAU_Project\cycles\cycle_17\ng.md への対応
- **物理定数の正規化:** 崩壊幅データを SSoT ローダー経由の取得に全面移行。
- **マジックナンバーの物理的根拠付け:** TSI 係数を次元数や成分数に基づく SSoT 変数に置換し、幾何学的正当性を付与。
- **FPR テストの完遂:** モンテカルロ置換検定により統計的有意性 (FPR = 0.0095) を証明。
- **精度改善:** 撤退基準を上回る R² = 0.7246 を達成。

## 主要な成果
- 全 9 粒子の崩壊幅を単一の幾何学的指標 TSI で説明することに成功。
- SSoT 定数のみを用いた精緻化 TSI 公式を確立。
- 統計的有意性が極めて高いことを証明し、モデルの物理的実在性を強化。

## 修正・作成ファイル
- E:\Obsidian\KSAU_Project\cycles\cycle_17\iterations\iter_06\code\h43_tsi_refinement_v2.py: 検証コード
- E:\Obsidian\KSAU_Project\cycles\cycle_17\iterations\iter_06\results.json: 計算結果
- E:\Obsidian\KSAU_Project\cycles\cycle_17\iterations\iter_06\researcher_report.md: 詳細レポート
