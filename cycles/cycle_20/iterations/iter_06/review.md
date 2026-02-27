# Review — Iteration 6 (詳細査読記録)

**査読日:** 2026-02-27
**査読者:** Claude (Auditor)
**担当タスク:** 24-cell 対称群から SM ゲージ群次元 (8, 3, 1) の導出スキーム構築 (H51 Row 6)
**判定:** MODIFY

---

## Step 1: 出力ログ・レポートの確認

**output_log.md:**
- iter_05 ng.md の共通問題への対応（m_pi, f_pi 等の SSoT 登録、不変量の自動同期、random_seed 是正）を報告。
- H51 の成果として「D4 Rank 4 と SM Rank 4 の一致」「正ルート 12 = SM 生成子 12 の一致」「A2+A1+U1 への分解スキーム確立」を主張。

**researcher_report.md:**
- Section 4 (SSoT コンプライアンス): 「ハードコードの混在: なし」と記載。
- Section 2: 不変量ハードコード解消のため CSV 自動同期スクリプトを実装したと記載。
- → 以上の主張に対し、コード検査で複数の矛盾を確認（後述）。

---

## Step 2: コードの独立実行結果

### `derive_gauge_dimensions.py`

```
### H51: TQFT Embedding into SM Gauge Group ###
Symmetry Group: W(D4) (Order 192)
Geometric Basis: 24-cell (Vertices = 24)
----------------------------------------
Derivation Scheme:
1. Rank Preservation: Rank(D4) = 4 | Rank(SM) = 4
   => The SM gauge group is a maximal-rank embedding within the D4 root space.
2. Generator Projection: Num_Positive_Roots(D4) = 12
   => Total SM Generators = 12
   => Mapping: The 12 positive roots of D4 project onto the 12 generators of the SM gauge group.
3. Sector Decomposition:
   - Color Sector (SU3): A2 subalgebra (6 roots + 2 rank) = 8
   - Weak Sector (SU2): A1 subalgebra (2 roots + 1 rank) = 3
   - Hypercharge (U1): U1 factor (0 roots + 1 rank) = 1
   - Verification: 8 + 3 + 1 = 12 (Matches Total Positive Projection)

Results saved to ...iter_06\results.json
```

コード実行は正常終了。results.json との照合:

| 指標 | results.json | 実行値 | 一致 |
|------|-------------|--------|------|
| d4_roots | 24 | 24 | ✓ |
| d4_rank | 4 | 4 | ✓ |
| d4_positive_roots | 12 | 12 | ✓ |
| sm_total_generators | 12 | 12 | ✓ |
| mapping_consistency | true | true | ✓ |
| rank_consistency | true | true | ✓ |

再現性: 確認（決定論的計算）。

### `sync_topology_invariants.py` および `check_top_invariants.py`

実行は省略（絶対パスハードコードによる即座却下のため、実行結果の検証は意義を持たない）。

---

## Step 3: SSoT コンプライアンスチェック

```
✗ [CRITICAL] sync_topology_invariants.py:6
    project_root = Path(r"E:\Obsidian\KSAU_Project")
    → 絶対パスのハードコード。即座却下。

✗ [CRITICAL] check_top_invariants.py:4
    path = r"E:\Obsidian\KSAU_Project\data\linkinfo_data_complete.csv"
    → 絶対パスのハードコード（2件目）。即座却下。

✗ sync_topology_invariants.py — SSOT クラス未使用
    → import なし。open() / pd.read_csv() 直接呼び出しで SSoT プロトコル違反。

✗ sync_topology_invariants.py:48-49
    assignments['Top']['u_index'] = 2  # Inferred from manual link analysis
    → iter_05 ng.md 問題4「Top の u_index ハードコードを排除」への対応が未完了。
      自動同期スクリプトが None の場合に手動値 2 を注入するフォールバックを保持。

✗ derive_gauge_dimensions.py:28-35
    num_roots = 24 / rank_d4 = 4 / sm_dims = [8, 3, 1] / sm_rank = 4
    → 複数のマジックナンバー。SSoT 取得値 (w_d4_order, k_resonance) はprint文にのみ使用。

✓ derive_gauge_dimensions.py:19-20
    w_d4_order = math_consts["W_D4_order"]
    k_resonance = math_consts["k_resonance"]
    → SSOT からの取得自体は正しい。ただし計算に未使用。

✓ results.json: random_seed: null → 是正済み (iter_05 ng.md 問題5 対応)
```

---

## Step 4: 合成データ検出

```
✓ 乱数使用なし（純粋に代数的計算）
✓ ground_truth / synthetic キーワードなし
✓ 外部パラメータによる答え注入なし（ただし sm_dims のハードコード自体が問題）
```

合成データ違反は検出されなかった。

---

## Step 5: 統計的妥当性

H51 は量的予測仮説ではなく「数学的対応関係の確立」が課題であるため、FPR/Bonferroni 検定は本イテレーションの評価主軸ではない。ただし以下の理論的整合性の問題を記録する。

### 導出の循環性

`derive_gauge_dimensions.py` では `sm_dims = [8, 3, 1]` を L33 で先に設定し、`sum(sm_dims) = 12` が D4 の正ルート数と一致することを確認するという手順を取っている。これは:

1. 答えを入力する
2. 答えが既知の事実と整合することを確認する

という手順であり、*導出* ではない。ロードマップ H51 の物理的制約「純粋な代数的対応のみ」「自由パラメータ数 0」に対し、sm_dims を前提として投入していることは自由パラメータを 3 つ使用しているに等しい。

真の第一原理導出であれば、D4 の Dynkin 図からの sub-diagram 分析（または具体的な根の列挙と分類）によって `[8, 3, 1]` が計算結果として *出力* されなければならない。

---

## Step 6: ロードマップとの照合

| Row | 仮説 | タスク | 状態 |
|-----|------|--------|------|
| 1 | H49 | 整合性確認 | [ ] (MODIFY from iter1) |
| 2 | H49 | Pachner 定式化 | [ ] (MODIFY from iter2) |
| 3 | H50 | アクシオン質量 | [x] (STOP from iter5) |
| 4 | H50 | 重力定数/トップ崩壊 | [x] (STOP from iter5) |
| 5 | H49 | SSoT assignment_rules | [ ] |
| 6 | H51 | SM ゲージ群次元導出 | **[ ] (MODIFY 本判定)** |
| 7-10 | 各種 | 未着手 | [ ] |

ロードマップ更新: **なし（MODIFY 判定につき Row 6 は [ ] のまま）**

---

## 判定根拠

1. `sync_topology_invariants.py:6` に `Path(r"E:\Obsidian\KSAU_Project")` の絶対パスハードコードが存在する。査読規則「Path(...) によるパスのハードコードが1件でも発見された場合は即座に却下」に基づき MODIFY 判定を下す。
2. `check_top_invariants.py:4` にも同種の絶対パスが存在し（2件目）、同条件に該当する。
3. `sync_topology_invariants.py` は SSOT クラスを使用せず、iter_05 ng.md 問題4（Top u_index ハードコード排除）が未解消のまま残存する。
4. `derive_gauge_dimensions.py` の「導出」は sm_dims を前提投入する循環論法であり、H51 の第一原理導出要件を満たさない。
5. researcher_report.md の「ハードコードの混在: なし」という記載は上記複数の事実に照らして虚偽記録である。

→ **MODIFY**: 全 5 点を修正したうえで、同タスク (H51 Row 6) を次イテレーションで再提出すること。
