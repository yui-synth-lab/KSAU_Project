# AIRDP Roadmap — KSAU Project Cycle 05

**作成日:** 2026-02-23
**Orchestrator:** Gemini-2.0-Flash (CLI-Agent)
**seed.md:** E:\Obsidian\KSAU_Project\cycles\cycle_01\seed.md

## 仮説一覧

| ID  | 仮説名 | 優先順位 | 最大イテレーション |
|-----|--------|----------|------------------|
| H9  | Geometric Scaling of Smallest Torsion (ST) | 高       | 5                |
| H11 | V=0 to V>0 Topological Phase Transition    | 高       | 5                |
| H10 | Hyperbolic Chern-Simons k-Function       | 中       | 5                |

## イテレーション割り当て表

**【Researcher へ】** 各イテレーション開始時に、この表の `[ ]` のうち最も若い番号の行を選び、その仮説IDとタスクを実行してください。
**【Reviewer へ】** 査読完了（CONTINUE または STOP 判定）後に、該当行の `[ ]` を `[x]` に更新してください。MODIFY 判定の場合は更新しないこと。

| Iter | 仮説ID | タスク概要 | 状態 |
|------|--------|-----------|------|
| 1    | H9     | Smallest Torsion (ST) と Volume V の相関データの抽出と初期回帰分析 | [x] |
| 2    | H9     | GPR モデルによる非線形スケーリングの検証と残差分析 | [x] |
| 3    | H11    | Torus (V=0) から Minimal Hyperbolic Volume (V>0) への相転移点の質量公式フィッティング | [x] |
| 4    | H11    | 電子・ミューオン質量比と理論的相転移ジャンプの整合性検証（LOO-CV） | [x] |
| 5    | H10    | Chern-Simons レベル k(V) の整数関数としての最適化（Witten 不変量基準） | [x] |
| 6    | H9     | Crossing number 別の Torsion scaling 安定性チェック | [x] |
| 7    | H11    | 第3世代（Tau）への拡張性と相転移モデルの汎用性テスト | [x] |
| 8    | H10    | k(V) マッピングの物理的解釈と不変量不整合の再評価 | [x] |
| 9    | H9     | Axion Suppression Model の最終的な統計的盾（Statistical Shield）構築 | [x] |
| 10   | H10    | 最終検証とプロジェクト全体への TQFT 整合性報告 | [x] |

> **ルール**: 優先順位が高い仮説を先に配置すること。ただし「高優先仮説がすべての配分を消費してしまう」ことを防ぐため、最高でも全体の 60% を単一仮説に割り当てないこと。

---

## 仮説 H9: Geometric Scaling of Smallest Torsion (ST)

### 帰無仮説 (H0)
Smallest Torsion $ln(ST)$ は Hyperbolic Volume $V$ と無相関であり、統計的に独立している（$R^2 < 0.5$）。

### 対立仮説 (H1)
Smallest Torsion $ln(ST)$ は $ln(ST) = \alpha V + \beta$（または GPR 同等モデル）に従い、$R^2 \ge 0.75$ で予測可能である。

### データ要件
KnotInfo/LinkInfo の 3-12 交点結び目データ、および SSoT constants.json の Axion Suppression Model パラメータを使用。

### 成功基準
- p値閾値: 0.05（Bonferroni補正前）
- Bonferroni補正後閾値: 0.016666
- 許容誤差: 5.0%以内
- 最小 R²: 0.75

### 撤退基準（削除不可）
- Bonferroni補正後 p > 0.016666 → 即座に REJECT
- FPR > 50% → 即座に REJECT
- 5 イテレーション到達で進展なし → REJECT
- Reviewer の連続 STOP 判定 2回 → 強制終了
- $R^2 < 0.5$ が確定した場合 → REJECT

### テスト手法
Gaussian Process Regression (GPR) および線形回帰分析。SSoT の `get_topology_constants` および `get_axion_suppression_model` を使用。

### 最大イテレーション数
5

---

## 仮説 H11: V=0 to V>0 Topological Phase Transition

### 帰無仮説 (H0)
電子 (V=0) から ミューオン (V>0) への質量差は、KSAU 質量公式および位相幾何学的相転移モデルでは説明できない（Error > 10%）。

### 対立仮説 (H1)
電子・ミューオン間の質量ギャップ $\Delta ln(m)$ は、Torus (V=0) と最小双曲体積 (V_min) の間の幾何学的断絶に由来し、誤差 5% 以内で一致する。

### データ要件
実粒子質量（constants.json）および双曲体積データ。

### 成功基準
- p値閾値: 0.05（Bonferroni補正前）
- Bonferroni補正後閾値: 0.016666
- 許容誤差: 5.0%以内
- 理論フィッティング R²: 0.99以上

### 撤退基準（削除不可）
- Bonferroni補正後 p > 0.016666 → 即座に REJECT
- FPR > 50% → 即座に REJECT
- 5 イテレーション到達で進展なし → REJECT
- Reviewer の連続 STOP 判定 2回 → 強制終了
- 誤差が 10% を超え、改善の見込みがない場合 → REJECT

### テスト手法
KSAU 質量公式の境界条件分析。SSoT の `get_physical_constants` および `get_topology_constants` を使用。

### 最大イテレーション数
5

---

## 仮説 H10: Hyperbolic Chern-Simons k-Function

### 帰無仮説 (H0)
Chern-Simons レベル $k$ は $V$ と独立している、または $Consistency Rate > 95\%$ を達成する $k(V)$ 整数関数は存在しない。

### 対立仮説 (H1)
$k(V) = \lfloor \alpha V + \beta floor$ 等の整数値関数が存在し、Witten 不変量との整合性レートが 95% を超える。

### データ要件
SSoT の `k_mapping_coefficients` および KnotInfo 結び目データ。

### 成功基準
- p値閾値: 0.05（Bonferroni補正前）
- Bonferroni補正後閾値: 0.016666
- Witten 整合性レート: 95.0%以上
- 非トートロジー的（自明な解ではないこと）

### 撤退基準（削除不可）
- Bonferroni補正後 p > 0.016666 → 即座に REJECT
- FPR > 50% → 即座に REJECT
- 5 イテレーション到達で進展なし → REJECT
- Reviewer の連続 STOP 判定 2回 → 強制終了
- 整合性レートが 80% を下回る場合 → REJECT

### テスト手法
全探索および最適化アルゴリズムによる $k(V)$ マッピング。SSoT の `get_k_mapping_coefficients` を使用。

### 最大イテレーション数
5

---

## リソース配分

| 仮説 | イテレーション配分 | 理由 |
|------|------------------|------|
| H9   | 4                | Axion Suppression の核心であり、物理的安定性の鍵となるため高配分。 |
| H11  | 3                | 世代間の質量的断絶の幾何学的由来を解明する上で重要。 |
| H10  | 3                | 以前のリジェクト結果（Cycle 04）を踏まえた改良版の検証。 |

## キュー（次サイクル候補）
- PMNS フレーバー混合の幾何学的導出（idea_queue.md）
- CKM Cabibbo禁止遷移のリンク不変量による抑制（idea_queue.md）
- ダークマター候補としての高次元双曲体積（idea_queue.md）

## 人間への確認事項
- **[Orchestrator補完]** H11 の Boundary について、シードファイルに明示的な記述がなかったため、プロジェクトコンテキストの「電子・ミューオン質量差は V=0 から V>0 への相転移」という原則に基づき補完しました。
- H10 について、Cycle 04 でのリジェクト結果を踏まえ、「$k=3$ 固定」ではなく「$k(V)$ 関数」へと改良していますが、この方向性で問題ないか。
- SSoT パス: **E:\Obsidian\KSAU_Project\ssot** を全 Researcher が参照することを確認してください。
