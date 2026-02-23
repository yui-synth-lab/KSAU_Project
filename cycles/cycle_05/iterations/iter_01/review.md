# Review — Iteration 1: MODIFY

**査読日:** 2026-02-23
**判定:** MODIFY

## 却下・修正要求の理由

### [問題1]: SSoT コンプライアンス違反（パスのハードコード）
**深刻度:** 致命的 (即却下対象)
**該当箇所:** 
- `task_h9_iter1.py:12`: `sys.path.insert(0, r"E:\Obsidian\KSAU_Project\ssot")`
- `task_h9_iter1.py:93`: `res_dir = Path(r"E:\Obsidian\KSAU_Project\cycles\cycle_05\iterations\iter_01")`
- `check_torsion.py:5`: `pd.read_csv(r'E:\Obsidian\KSAU_Project\data\knotinfo_data_complete.csv', ...)`
**問題の内容:** プロジェクト規定および査読基準で厳禁とされている `Path("...")` 等による絶対パスの直接記述（ハードコード）が複数箇所で確認されました。
**要求する対応:** 全てのパスを直接書かず、プロジェクト規定（Rule 4）に従い、コード冒頭で `SSOT_DIR = Path("E:\Obsidian\KSAU_Project\ssot")` を定義した上で、それを基準とした相対的な構築に修正してください。また、データへのアクセスは必ず SSoT ローダーを介してください。

### [問題2]: SSoT ローダーのバイパス
**深刻度:** 重大
**該当箇所:** `check_torsion.py:5`
**問題の内容:** `pd.read_csv` を使用して CSV ファイルを直接読み込んでいます。これは「すべてのデータは SSoT から取得すること」という原則（Rule 2）に反します。
**要求する対応:** `check_torsion.py` を削除するか、SSoT ローダーを使用するように修正してください。

### [問題3]: 統計的検証（FPR テスト）の欠如
**深刻度:** 重大
**該当箇所:** `researcher_report.md`, `results.json`
**問題の内容:** 査読基準 Step 5 で「必須」とされている FPR テスト（Monte Carlo null test）の結果が報告されていません。$R^2 = 0.3561$ という結果が、ランダムな割り当て（帰無仮説）と比較してどの程度有意であるかを定量的（FPR）に示す必要があります。
**要求する対応:** 10,000回以上のランダム・シャッフルによる Monte Carlo シミュレーションを実行し、FPR を算出して報告してください。

### [問題4]: SSoT パス定義の形式不備
**深刻度:** 軽微
**該当箇所:** `task_h9_iter1.py` 冒頭
**問題の内容:** プロジェクト規定（Rule 4）にある `SSOT_DIR = Path("<パス>")` の形式での定義が欠落しています。
**要求する対応:** 規定通りの形式で定義してください。

## 統計指標
- p 値（観測）: 0.00e+00
- Bonferroni 補正後閾値: 0.016666
- FPR: 未計算 (要修正)
- 判定根拠: パスのハードコード（即却下対象）および検証不足。
