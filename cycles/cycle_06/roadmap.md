# AIRDP Roadmap — KSAU Project Cycle 06

**作成日:** 2026-02-23
**Orchestrator:** Gemini-2.0-Flash-Thinking-exp
**seed.md:** E:\Obsidian\KSAU_Project\cycles\cycle_01\seed.md

## 事前スクリーニング記録

- **H12 (Axion ST 実データ検証):** 
    - [x] 定量的検証可能か？: $\Delta \log_{10}(ST) \leq 2$ という明確な基準あり。
    - [x] 否定的結果と重複していないか？: Jones多項式の棄却（NEG-20260222-01）を反映し、有効な幾何学変量のみを使用。合成データでの成功（constants.json）を実データで検証する段階。
    - [x] 現在の探索スコープ内か？: アクシオン抑制因子の精度向上は v7.0 の核心。
    - [x] 実データで検証可能か？: `topology_assignments.json` の実不変量を使用可能。
- **H13 (WRTベース TQFT 写像):**
    - [x] 定量的検証可能か？: Witten 整合性レート $> 80\%$ という基準あり。
    - [x] 否定的結果と重複していないか？: 線形モデルの棄却（NEG-20260222-02, NEG-20260223-03）を受け、非線形・WRTベースのアプローチへ移行。
    - [x] 現在の探索スコープ内か？: TQFT との数学的整合性確保は理論基盤強化に必須。
    - [x] 実データで検証可能か？: SSoT の不変量データから算出可能。

## 仮説一覧

| ID | 仮説名 | 優先順位 | 最大イテレーション |
|----|--------|----------|------------------|
| H12 | Axion ST 実データ検証 | 高 | 3 |
| H13 | WRTベース TQFT 写像 | 高 | 2 |

## イテレーション割り当て表

**【Researcher へ】** 各イテレーション開始時に、この表の `[ ]` のうち最も若い番号の行を選び、その仮説IDとタスクを実行してください。
**【Reviewer へ】** 査読完了（CONTINUE または STOP 判定）後に、該当行の `[ ]` を `[x]` に更新してください。MODIFY 判定の場合は更新しないこと。

| Iter | 仮説ID | タスク概要 | 状態 |
|------|--------|-----------|------|
| 1    | H12    | [H12-I1] SSoT 実データに基づくベースライン GPR モデルの構築と R² 評価 | [x] |
| 2    | H12    | [H12-I2] 幾何学不変量 (V, Det, Sig) の非線形項導入による不確定性縮小試行 | [x] |
| 3    | H12    | [H12-I3] 最終モデルの $\Delta \log_{10}(ST)$ 定量化と感度分析 | [x] |
| 4    | H13    | [H13-I1] 非線形パリティシフト写像モデルの構築と Witten 整合性評価 | [x] |
| 5    | H13    | [H13-I2] WRT不変量の近似導入による写像の非トートロジー性検証 | [x] |

> **ルール**: 優先順位が高い仮説を先に配置すること。H12 は実用上の緊急性が高いため 60% (3/5) を割り当て、H13 は理論的挑戦として 40% (2/5) を割り当てる。

---

## 仮説 H12: Axion ST 実データ検証 (Refined H2)

### 帰無仮説 (H0)
実データ（topology_assignments.json）において、幾何学的不変量とアクシオン抑制因子 ST の間に有意な相関が認められない（$R^2 < 0.5$）か、または対数不確定性を $\Delta \log_{10}(ST) \leq 2$ まで縮小できない。

### 対立仮説 (H1)
実データに基づく非線形幾何学モデル（GPR等）により、$R^2 \geq 0.5$ を維持しつつ、アクシオン抑制因子の不確定性を $\Delta \log_{10}(ST) \leq 2$ まで縮小可能である。

### データ要件
- `ssot/data/raw/topology_assignments.json`（Volume, Determinant, Crossing Number, Generation）
- `ssot/constants.json`（axion_suppression_model 統計基準）

### 成功基準
- p値閾値: 0.05（Bonferroni補正前）
- Bonferroni補正後閾値: 0.025（= 0.05 / 2 仮説数）
- 許容誤差: $\Delta \log_{10}(ST) \leq 2.0$
- 最小 R²: 0.5

### 撤退基準（削除不可）
- Bonferroni補正後 p > 0.025 → 即座に REJECT
- FPR > 50% → 即座に REJECT
- 3 イテレーション到達で $\Delta \log_{10}(ST) \leq 2$ 未達 → REJECT
- Reviewer の連続 STOP 判定 2回 → 強制終了

### テスト手法
- ガウス過程回帰 (GPR) による不確定性区間算出（Maternカーネル推奨）。
- 交差検証 (LOO-CV) による汎化性能評価。

### 最大イテレーション数
3

---

## 仮説 H13: WRTベース TQFT 写像 (Refined H3)

### 帰無仮説 (H0)
CSレベル $k$ への写像 $k(T)$ が、Witten 整合性（$Det(K) \mod k = 0$ プロキシ等）を 80% 以上のレートで満たさない、または写像が双曲体積 $V$ との単純な線形相関（$r \geq 0.95$）に留まる。

### 対立仮説 (H1)
非線形、あるいはパリティシフトを考慮した代数的写像により、Witten 整合性レート $> 80\%$ を達成し、かつ体積 $V$ とは独立した（$r < 0.95$）非トートロジーな $k$ 定義が可能である。

### データ要件
- `ssot/data/raw/topology_assignments.json`（Determinant, Volume, Crossing Number）
- `ssot/constants.json`（k_mapping_coefficients, statistical_thresholds）

### 成功基準
- p値閾値: 0.05（Bonferroni補正前）
- Bonferroni補正後閾値: 0.025（= 0.05 / 2 仮説数）
- Witten 整合性レート: $> 80\%$
- 非トートロジー条件: $r(V, k) < 0.95$

### 撤退基準（削除不可）
- Bonferroni補正後 p > 0.025 → 即座に REJECT
- FPR > 50% → 即座に REJECT
- 2 イテレーション到達で整合性レート改善なし → REJECT
- Reviewer の連続 STOP 判定 2回 → 強制終了

### テスト手法
- 離散写像関数の構築と Witten 条件の全域評価。
- Monte Carlo 置換検定による統計的有意性検証。

### 最大イテレーション数
2

---

## リソース配分

| 仮説 | イテレーション配分 | 理由 |
|------|------------------|------|
| H12 | 3 | 合成データでの成功を実証段階へ移行させるため、重点的に割り当てる。 |
| H13 | 2 | 線形モデルの限界を超越するための探索的フェーズ。 |

## キュー（次サイクル候補）
- PMNS ニュートリノ混合の再検討（seed.md より）
- CKM Cabibbo-forbidden 要素の改善（seed.md より）

## 人間への確認事項
- H13 における WRT 不変量の直接計算が必要になった場合、外部ライブラリ（SnapPy等）の導入を許可するか？現時点では SSoT 内の不変量で代用する。
