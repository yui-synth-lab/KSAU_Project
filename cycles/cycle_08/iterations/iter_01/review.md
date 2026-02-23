# Review — Iteration 1: MODIFY

**査読日:** 2026-02-23
**判定:** MODIFY

## 却下・修正要求の理由

### [問題1]: SSoT コンプライアンス違反（パスのハードコード）
**深刻度:** 致命的
**該当箇所:** 
- `derive_kappa.py:8`: `sys.path.insert(0, r"E:\Obsidian\KSAU_Project\ssot")`
- `derive_kappa.py:59`: `Path("E:/Obsidian/KSAU_Project/cycles/cycle_08/iterations/iter_01/results.json")`
**問題の内容:** 絶対パスがコード内に直接書き込まれています。プロジェクト規約および Reviewer 査読基準（Step 3）により、絶対パスのハードコードは即却下対象です。
**要求する対応:** `Path(__file__)` からの相対パス、または環境変数、あるいは `ksau_ssot` モジュールが提供するパス取得機能を利用し、ハードコードを排除してください。

### [問題2]: 統計的妥当性の検証不足（FPR テストの欠如）
**深刻度:** 重大
**該当箇所:** `results.json`, `derive_kappa.py`
**問題の内容:** ロードマップの撤退基準（FPR > 50%）を判定するための FPR テスト（Monte Carlo null test）が実施されていません。理論的導出であっても、その数式（$\pi/24$）が偶然一致する確率を評価する必要があります。
**要求する対応:** $\kappa$ の理論値に対する Monte Carlo 法等を用いた FPR 評価コードを追加し、`results.json` に記録してください。

### [問題3]: データの真正性と整合性の不備
**深刻度:** 軽微
**該当箇所:** `derive_kappa.py:16`, `results.json:28`
**問題の内容:** `results.json` では `constants_used` に `pi` を含めていますが、コード内では SSoT の `pi` ではなく `np.pi` を使用しています。また、`k_res = 24` がマジックナンバーとしてハードコードされています。
**要求する対応:** 
1. `pi` は必ず SSoT (`consts['mathematical_constants']['pi']`) から取得してください。
2. `24` という定数に理論的根拠（24-cell 等）をリンクさせるか、可能であれば SSoT への定義追加を検討してください。

### [問題4]: 「理論的導出」の不十分さ
**深刻度:** 重大
**該当箇所:** `researcher_report.md`
**問題の内容:** タスクは「理論的導出」ですが、現状は SSoT 値と理論値の一致を確認（Verification）したに留まっています。なぜ 24 なのか、なぜ $\pi$ なのかという幾何学的必然性の説明がレポートにおいて抽象的です。
**要求する対応:** Pachner move と位相共鳴の関係を、Chern-Simons 理論等の枠組みと関連付けてより具体的に記述してください。

## 統計指標
- p 値（観測）: 未計算
- Bonferroni 補正後閾値: 適用外（単一検証）
- FPR: 未計算（判定不可）
- 判定根拠: SSoT コンプライアンス違反（絶対パス・マジックナンバー）および検証プロセス不足。
