# Seed: Cycle 17 — Holistic Mass Unification and Decay Dynamics

**作成日:** 2026-02-26
**Status:** DRAFT（人間による精査・承認待ち）
**引き継ぎ元:** Cycle 16 / cycle_report.md

---

## 1. 核心的な問い (Core Questions)

1. **レプトンセクターにおける $V_{eff}$ 逆転の解消:** Muon と Tau の有効体積 $V_{eff}$ の逆転（Muon > Tau）を、追加のトポロジカル不変量（例: Torsion, Jones Polynomial root, etc.）によって理論的に解消できるか？
2. **ボソンセクターの系統的シフトの幾何学的根拠:** ボソン質量の予測値が系統的に約 +5.5 ln シフトする現象は、Brunnian link の特異的な連結構造（Component count = 3）から幾何学的に導出可能か？
3. **崩壊幅 Γ と TSI (Topological Stability Index) の普遍的相関:** TSI 定義の改善により、全フェルミオンおよびボソンセクターにわたる崩壊幅の回帰モデルを R² > 0.8 で安定化できるか？

---

## 2. 理論的背景

1. **κ の第一原理確定:** Cycle 16 (H39) により、$\kappa = \pi/24$ が 24-cell (Octaplex) の幾何学的共鳴条件から導出され、SSoT に統合された。
2. **統一モデルの限界 (H40):** 全 12 粒子の統一回帰は棄却された。主な原因はレプトンセクターの $V_{eff}$ 逆転と、ボソンセクターの正の系統的オフセットであることが判明。
3. **有効体積モデルの深化:** 現行の $V_{eff} = V + a \cdot n + b \cdot \ln(det) + c$ はフェルミオン質量（クォーク・電子）には適合するが、Muon/Tau およびボソンに対しては不十分である。

---

## 3. MODIFY 差し戻し仮説（Judge 修正指示）

> **この節は Judge の verdict.md から直接引き継ぐ。Orchestrator による解釈・省略は禁止。**

*Cycle 16 において MODIFY 判定を受けた仮説はありませんでした。*

---

## 4. 新規探索候補

### H41: Geometric Correction for Lepton Sector Mass Inversion
- **仮説:** レプトンセクターの $V_{eff}$ には、世代に依存する位相幾何学的「ねじれ（Torsion）」または「絡み数（Linking number）」による補正項 $\Delta V_{lep}$ が加わり、$\ln(m) = \kappa (V_{eff} + \Delta V_{lep})$ となる。
- **目標:** $R^2 > 0.99$, 全粒子 MAE < 5%

### H42: Systematic Shift of Boson Sector (Component-based Scaling)
- **仮説:** 自由エネルギースケーリングは成分数 $C$ に依存し、ボソン（$C=3$, Brunnian）に対しては $\Delta \ln(m) \approx 5.5$ の定数シフトが発生する。
- **根拠:** SSoT のボソンスケーリング定数 $C=5.5414$ とボソンの成分数 3 の関係性の探索。

### H43: Decay Width Correlation via Refined TSI
- **仮説:** TSI 定義 ($n \cdot u / |s|$) をさらに精緻化し、崩壊幅 $\Gamma$ との対数線形相関モデルを PDG 全データに対して検証する。
- **優先度:** 高（idea_queue より）

---

## 5. Boundary（失敗条件・撤退基準）

| 条件 | 処理 |
|------|------|
| 科学的整合性違反（過学習・チェリーピッキング・事後的カーブフィッティング） | 即座に MODIFY |
| Bonferroni 補正後 p > 閾値 (0.01) | REJECT |
| FPR > 50% | REJECT |
| Reviewer 連続 STOP 2 回 | 強制終了 |
| 最大イテレーション到達で進展なし | REJECT |
