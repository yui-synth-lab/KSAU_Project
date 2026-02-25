# Seed: Cycle 15 — Topological Correlates of Stability and Mass Residuals

**作成日:** 2026-02-25
**Status:** DRAFT（人間による精査・承認待ち）
**引き継ぎ元:** Cycle 14 / cycle_report.md

---

## 1. 核心的な問い (Core Questions)

1. **崩壊幅の幾何学的規定**: 結び目多様体の位相不変量（Crossing Number, Signature 等）は、素粒子の崩壊幅 Γ (または寿命 τ) を統計的に有意に説明できるか？
2. **質量残差の線形補正**: 第1次近似 $\ln(m) = \kappa V_{eff} + C$ の残差に対し、トポロジカル・トーション ($\ln ST$) による**線形**補正を導入することで、過学習を避けつつ予測精度を向上できるか？

---

## 2. 理論的背景

- **κ の理論的確立**: Cycle 14 (H36) において、κ = π/24 は 24-cell (24胞体) の対称性から必然的に導出されることが示された。
- **有効体積モデルの成功**: Cycle 14 (H35) により、副次的な幾何パラメータ (n, ln_det) を含む $V_{eff}$ モデルが質量予測 $R^2$ を 0.8577 まで向上させ、κ の不偏性を証明した。
- **寿命相関の既知実績**: Cycle 08 (H17) では寿命 τ と TSI ($n \cdot u / |s|$) の相関が $R^2 = 0.991$ で得られており、崩壊幅 Γ への拡張は自然な理論展開である。

---

## 3. MODIFY 差し戻し仮説（Judge 修正指示）

> **この節は Judge の verdict.md から直接引き継ぐ。Orchestrator による解釈・省略は禁止。**

**本サイクルに MODIFY 判定の差し戻し案件はありません。**

---

## 4. 新規探索候補

### H37: Correlation between Decay Width and Knot Invariants
- **アイデア:** PDG (Particle Data Group) の崩壊幅 Γ データを SSoT に統合し、Crossing Number, Unknotting Number, Signature との相関を重回帰分析で検証する。
- **期待される成果:** 粒子の安定性が幾何学的複雑性と直結していることの立証。

### H38: Linear Topological Torsion Correction for Mass Residuals
- **アイデア:** Cycle 14 (H34) の REJECT 理由（過学習および有意性不足）を克服するため、全フェルミオン 9 点に対する**自由度を 2 (α, β) に制限した線形モデル** $\Delta \ln(m) = \alpha \ln(ST) + \beta$ を検証する。
- **設計制約:** パラメータ数を 2 個以下に限定し、自由度 $df \ge 7$ を確保すること。

---

## 5. Boundary（失敗条件・撤退基準）

| 条件 | 処理 |
|------|------|
| 科学的整合性違反（過学習・チェリーピッキング・事後的カーブフィッティング） | 即座に MODIFY |
| Bonferroni 補正後 p > 0.025 (H37, H38 の 2 仮説) | REJECT |
| FPR > 50% | REJECT |
| Reviewer 連続 STOP 2 回 | 強制終了 |
| 最大イテレーション (10) 到達で進展なし | REJECT |
