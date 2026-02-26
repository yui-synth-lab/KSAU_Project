# Seed: Cycle 18 — Geometric Resonance and Torsion Refinement

**作成日:** 2026-02-26
**Status:** DRAFT（人間による精査・承認待ち）
**引き継ぎ元:** Cycle 17 / cycle_report.md

---

## 1. 核心的な問い (Core Questions)

1. $\kappa = \pi/24$ における「24」という数値の理論的必然性を、24-cell 幾何学や Pachner move の共鳴条件から導出できるか？
2. 全フェルミオン 9 点の質量残差を、Smallest Torsion (ST) 項の線形導入によって、統計的有意義性（Bonferroni 補正後 p < 0.0167）を保ちつつ改善できるか？

---

## 2. 理論的背景

Cycle 17 において、レプトン質量逆転の解消（$\alpha=2.5$）およびボソン切片の幾何学的導出（$C_{boson} \approx 5.541 = \pi \sqrt{3} + 0.1$）に成功した。これにより、12 粒子すべての質量を統一的な幾何学作用（Effective Volume）で記述する基盤が整った。特にボソン切片が幾何学的定数から導出できたことは、質量勾配 $\kappa = \pi/24$ の分母「24」についても、単なるフィッティングパラメータではなく、理論的必然（例：24-cell 幾何学的対称性）として導出できる可能性を強く示唆している。

---

## 3. MODIFY 差し戻し仮説（Judge 修正指示）

> **この節は Judge の verdict.md から直接引き継ぐ。Orchestrator による解釈・省略は禁止。**

該当なし（Cycle 17 の全仮説が ACCEPT 判定）。

---

## 4. 新規探索候補

### H44: Theoretical Derivation of the "24" in $\kappa = \pi/24$
- **内容:** Pachner move 1回あたりの作用を $\kappa$ と定義し、共鳴条件 $K(4) \cdot \kappa = \pi$ における $K(4)$ が、10次元バルク内の 24-cell 対称性（D4 格子、24 頂点）から 24 となることを検証する。
- **目的:** フィッティングパラメータ $\kappa$ を理論定数へと昇格させる。

### H45: Linear ST Correction for All Fermions
- **内容:** Cycle 10 で過学習により棄却された ST 補正（H23）を再設計。全フェルミオン 9 点に対し、$\ln(m) = \kappa V_{eff} + A \ln(ST) + B$ という**線形**モデルを適用する。
- **制約:** 自由度 $df = 9 - 2 = 7$ を確保し、統計的有意義性を最優先する。

---

## 5. Boundary（失敗条件・撤退基準）

| 条件 | 処理 |
|------|------|
| 科学的整合性違反（過学習・チェリーピッキング・事後的カーブフィッティング） | 即座に MODIFY |
| Bonferroni 補正後 p > 閾値 | REJECT |
| FPR > 50% | REJECT |
| Reviewer 連続 STOP 2 回 | 強制終了 |
| 最大イテレーション到達で進展なし | REJECT |
