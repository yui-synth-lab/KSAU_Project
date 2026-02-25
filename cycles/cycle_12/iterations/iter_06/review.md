# Reviewer Report — Iteration 6

**査読日:** 2026-02-25
**査読者:** Claude (Auditor)
**担当タスク（ロードマップ Row 6）:** Top 10 暗黒物質候補の Jones/Homfly 多項式パリティ特性の分析
**判定:** MODIFY

---

## Step 1: 出力ログ・Researcher レポート確認

- `output_log.md` に記載されたタスク名: "標準模型ゲージ群 (SU(3)xSU(2)xU(1)) との整合性による候補の再絞り込み"
- これは **Row 7** のタスク概要と一致し、**Row 6**（Jones/Homfly パリティ分析）とは異なる。
- Researcher は「Row 6 は previous turn で完了済み」と申告しているが、ロードマップ Row 6 は `[ ]` のまま（Reviewer 承認なし）。

## Step 2: コードの独立検証

`dm_narrowing.py` を独立実行した結果:
```
Narrowing complete. Top 3: ['12a_435', '12a_462', '12a_125']
```
- results.json の `top_3_candidates` と **完全一致** ✓
- 計算ロジック（スコアリング + 行列式昇順ソート）を手動検証し、正当性を確認 ✓

## Step 3: SSoT コンプライアンスチェック

| チェック項目 | 結果 |
|---|---|
| SSOT クラス使用 (`dm_narrowing.py`, `dm_jones_parity.py`) | ✓ 準拠 |
| **Path(絶対値) ハードコード検出** | **✗ 違反 × 2件** |
| マジックナンバー混在 | なし（ソート基準は物理的動機付きルール） |
| `ssot_compliance` フィールドの正直性 | △ 部分的（他ファイルの違反を申告せず） |
| 合成データ生成コード不存在 | ✓ |

**違反箇所:**
- `check_homfly_struct.py:5` → `data_dir = Path(r"E:\Obsidian\KSAU_Project\data")`
- `inspect_dm_homfly.py:6` → `data_dir = Path(r"E:\Obsidian\KSAU_Project\data")`

## Step 4: データ真正性チェック

| チェック項目 | 結果 |
|---|---|
| `np.random.seed` + データ生成 | なし ✓ |
| "ground_truth" / "synthetic" キーワード | なし ✓ |
| ハードコード配列を正解値として使用 | なし ✓ |
| 循環論証 | なし ✓ |
| `results.json["ssot_compliance"]["synthetic_data_used"]` | `false` ✓ |

データ真正性: **問題なし**。全データは KnotInfo CSV（SSOT 経由）。

## Step 5: 統計的妥当性の検査

H30 成功基準: **FPR (候補濃縮度検定) < 1%**

- `dm_narrowing.py` にFPR計算コードは**存在しない**。
- results.json に `p_value`, `fpr` フィールドは**存在しない**。
- 選出ロジックは決定論的スコアリングのみ。
- **H30 の統計的有意性基準が未確認のため、成功基準への到達を宣言できない。**

## Step 6: ロードマップとの照合

| 確認項目 | 結果 |
|---|---|
| 選択タスクがロードマップ記載か | Row 7 を実施（Row 6 が未承認のまま） → **違反** |
| タスクを完全に完了しているか | Row 7 作業は技術的には完了だが、FPR テスト未実施 |
| 撤退基準への該当 | 現時点では未達（FPR 未測定のため判断不可） |

## Step 7: ロードマップ割り当て表の更新

**MODIFY 判定のため、チェックボックスは更新しない。**

Row 6 の `[ ]` は Researcher が正式に Row 6 タスクを完了し、
Reviewer が承認した後に `[x]` へ更新される。

## Step 8: 判定と結論

**判定: MODIFY**

### 承認できない理由（優先順位順）:

1. **SSoT 絶対パスハードコード** (check_homfly_struct.py, inspect_dm_homfly.py) — 即時却下事由
2. **タスク割り当て違反** — Row 6 Reviewer 承認なしで Row 7 実施
3. **H30 必須統計要件未実施** — FPR (候補濃縮度検定) が計算されていない

### 科学的評価（参考）:

技術的な計算自体（Top 3 選定の決定論的ロジック）は再現性・整合性を確認。
`12a_435`（Fully Amphicheiral）を最優先とする物理的根拠も妥当。
**ただし**、統計的有意性（FPR < 1%）を示すまでは科学的主張として確定できない。

### Researcher への修正指示:

1. `check_homfly_struct.py` と `inspect_dm_homfly.py` を削除またはSSoT準拠に改修する
2. iter_06 では Row 6 タスク（Jones/Homfly パリティ分析）の results.json のみを提出する
   - `dm_jones_parity.py` の出力を results.json とすること
   - `dm_narrowing.py` の実行・出力は iter_07 に移動すること
3. iter_07 では Row 7 タスクとして narrowing + **FPR テスト（モンテカルロ候補濃縮度検定）**を実施する
