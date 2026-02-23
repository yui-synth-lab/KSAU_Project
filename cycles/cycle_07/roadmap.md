# AIRDP Roadmap — KSAU Cycle 07

**作成日:** 2026-02-23
**Orchestrator:** Gemini 2.0 Flash
**seed.md:** E:\Obsidian\KSAU_Project\cycles\cycle_01\seed.md

## 仮説一覧

| ID | 仮説名 | 優先順位 | 最大イテレーション |
|----|--------|----------|------------------|
| H14 | Axion ST Uncertainty Reduction (GPR-Refined) | 高 | 5 |
| H15 | Algebraic Mapping to TQFT CS Level (Discrete) | 中 | 5 |

## イテレーション割り当て表

**【Researcher へ】** 各イテレーション開始時に、この表の `[ ]` のうち最も若い番号の行を選び、その仮説IDとタスクを実行してください。
**【Reviewer へ】** 査読完了（CONTINUE または STOP 判定）後に、該当行の `[ ]` を `[x]` に更新してください。MODIFY 判定の場合は更新しないこと。

| Iter | 仮説ID | タスク概要 | 状態 |
|------|--------|-----------|------|
| 1    | H14    | GPR モデル의ベースライン評価と Jones 不変量の再検証 | [x] |
| 2    | H14    | 非線形カーネルを用いた不確定性 Δlog₁₀(ST) の最小化 | [x] |
| 3    | H15    | 離散的量子化アルゴリズムによる CS 写像の初期設計 | [x] |
| 4    | H15    | Witten 合同条件に基づく写像の整合性テスト | [x] |
| 5    | H14    | 不確定性予測の外部データセットによる交差検証 | [x] |
| 6    | H15    | 非トートロジー相関 (r < 0.95) の統計的有意性検定 | [x] |
| 7    | H14    | 最終的な Δlog₁₀(ST) 縮小効果の定量評価と報告 | [x] |
| 8    | H15    | TQFT 不変量との物理的整合性最終チェック | [x] |

> **ルール**: 優先順位が高い仮説を先に配置すること。ただし「高優先仮説がすべての配分を消費してしまう」ことを防ぐため、最高でも全体の 60% を単一仮説に割り当てないこと。

---

## 仮説 H14: Axion ST Uncertainty Reduction (GPR-Refined)

### 帰無仮説 (H0)
幾何学的不変量（V, Det, J）を用いても、アクシオン抑制因子 ST の対数不確定性を Δlog₁₀(ST) ≤ 2 まで縮小できない、または相関が統計的に有意でない (p > 0.025)。

### 対立仮説 (H1)
ガウス過程回帰 (GPR) 等の非線形モデルを用いることで、幾何学的不変量から ST の不確定性を Δlog₁₀(ST) ≤ 2 まで縮小可能であり、かつ R² ≥ 0.5 を達成する。

### データ要件
- KnotInfo 実データ（V, Det, Signature, Jones Polynomial 評価値）
- 参照: E:\Obsidian\KSAU_Project\ssot\constants.json (`axion_suppression_model_gpr`)

### 成功基準
- p値閾値: 0.05（Bonferroni補正前）
- Bonferroni補正後閾値: 0.025（= 0.05 / 2 仮説数）
- 許容誤差: Δlog₁₀(ST) ≤ 2.0
- 最小 R²: 0.5

### 撤退基準（削除不可）
- Bonferroni補正後 p > 0.025 → 即座に REJECT
- FPR > 50% → 即座に REJECT
- 5 イテレーション到達で進展なし → REJECT
- Reviewer の連続 STOP 判定 2回 → 強制終了
- [Orchestrator補完] R² < 0.2 が継続し、モデル改善の余地がない場合 → REJECT

### テスト手法
実データを用いた GPR (Gaussian Process Regression) による不確定性予測 (95% 予測区間の幅を評価)。Jones 不変量については NEG-20260222-01 の結果を考慮し、非線形結合のみを探索する。

### 最大イテレーション数
5

---

## 仮説 H15: Algebraic Mapping to TQFT CS Level (Discrete)

### 帰無仮説 (H0)
粒子トポロジーから CS レベル k への物理的に整合した（Witten 条件を満たす）写像を構築できない、あるいは構築された写像が V とのトートロジー (r ≥ 0.95) である。

### 対立仮説 (H1)
離散的量子化アルゴリズムを用いることで、Witten 合同条件 (`Det(K) mod k == 0` 等) を 80% 以上のレートで満たし、かつ V との相関が r < 0.95 である非自明な写像を定義可能である。

### データ要件
- SSoT 記載のトポロジー定数および不変量
- 参照: E:\Obsidian\KSAU_Project\ssot\constants.json (`k_mapping_coefficients`)

### 成功基準
- p値閾値: 0.05
- Bonferroni補正後閾値: 0.025
- Witten 整合性レート: > 80%
- 非トートロジー条件: r < 0.95

### 撤退基準（削除不可）
- Bonferroni補正後 p > 0.025 → 即座に REJECT
- FPR > 50% → 即座に REJECT
- 5 イテレーション到達で進展なし → REJECT
- Reviewer の連続 STOP 判定 2回 → 強制終了
- [Orchestrator補完] 写像が Witten 条件を満たしつつも、物理的に解釈不可能なパラメータ空間に限定される場合 → REJECT

### テスト手法
離散関数写像の評価。順列検定による有意性確認 (FPR 算出)。NEG-20260223-04 の教訓に基づき、単純な線形・連続モデルではなく、Jones 多項式の根の構造を反映した離散アルゴリズムを採用する。

### 最大イテレーション数
5

---

## リソース配分

| 仮説 | イテレーション配分 | 理由 |
|------|------------------|------|
| H14 | 4 (50%) | 実験感度への直接的な寄与が高いため、優先的に配分。 |
| H15 | 4 (50%) | 理論的基盤の確立に不可欠だが、過去の失敗経験（H13）を踏まえ、慎重に配分。 |

## キュー（次サイクル候補）
- PMNS ニュートリノ混合の再検討（seed.md より）
- CKM Cabibbo-forbidden 要素の改善（seed.md より）

## 人間への確認事項
- H14 において、J(e^{2πi/5}) が単独で有意でないことが判明しているが、非線形カーネル内での使用を継続するか？（Orchestrator は「継続」と判断し、交互作用を含めた探索を Researcher に指示する予定）
