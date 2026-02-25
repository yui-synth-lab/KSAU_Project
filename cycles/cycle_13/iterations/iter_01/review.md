# Review — Iteration 1: MODIFY

**査読日:** 2026年02月25日
**判定:** MODIFY

## 却下・修正要求の理由

### [問題1]: FPR テスト（モンテカルロ置換検定）の欠落
**深刻度:** 致命的
**該当箇所:** results.json, baseline_regression.py
**問題の内容:** 査読手順 Step 5 および統計的妥当性基準において「FPR テスト（必須）」と明記されているが、実装コードおよび結果ファイルに帰無仮説シミュレーション（Monte Carlo null test）による FPR の算出が含まれていない。
**要求する対応:** 10,000 回の置換検定（Permutation Test）を実装し、FPR を算出して results.json に記録すること。

### [問題2]: パスのハードコード（SSoT コンプライアンス違反）
**深刻度:** 重大
**該当箇所:** baseline_regression.py:19, baseline_regression.py:108
**問題の内容:** 査読手順 Step 3 において「Path("...") 等のパスがコード内に存在しないか？（1件でも即却下）」と定められているが、絶対パスが直接記述されている。
- L19: `sys.path.insert(0, r"E:\Obsidian\KSAU_Project\ssot")`
- L108: `output_path = Path("E:/Obsidian/KSAU_Project/cycles/cycle_13/iterations/iter_01/results.json")`
**要求する対応:** これらのパスをハードコードせず、相対パスや実行時のディレクトリ情報、またはプロジェクト構成に基づく定数（SSOT_DIR 等）から導出するように修正すること。

### [問題3]: データのハードコード選択
**深刻度:** 軽微
**該当箇所:** baseline_regression.py:20-21
**問題の内容:** 分析対象の粒子リスト（`quarks`, `leptons`）がコード内に直接列挙されている。
**要求する対応:** SSoT（`params['quarks'].keys()` 等）から動的に取得するように変更し、コードの汎用性と SSoT への依存度を高めること。

### [問題4]: レプトン・スケールの抽出ロジックの脆弱性
**深刻度:** 軽微
**該当箇所:** baseline_regression.py:25
**問題の内容:** `lepton_jump_str.split("*")[0]` という文字列操作でスケールを取得しているが、SSoT の記述形式変更に弱く、マジックナンバーに近い。
**要求する対応:** より堅牢な正規表現による抽出、あるいは SSoT (constants.json) 側で `lepton_jump_scale: 20` のように数値として定義・取得することを推奨。

## 統計指標
- p 値（Quark 回帰）: 0.001697
- p 値（Unified 回帰）: 0.004617
- Bonferroni 補正後閾値: 0.016666
- FPR: 未計測（要修正）
- 判定根拠: FPR 未計測および実装上のコンプライアンス違反（ハードコード）のため。また、統一モデルの 95% 信頼区間に理論値 κ が含まれておらず、撤退基準に抵触するリスクがあるため、モデルの精査が必要。
