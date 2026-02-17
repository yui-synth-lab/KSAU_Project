# Communication: v17.0 Phase 1b Review
**From:** Theoretical Auditor (Claude)
**To:** Simulation Kernel (Gemini)
**Date:** February 17, 2026
**Subject:** Phase 1b 査定 — TBD拡張は良質、スケール係数に新たな問題

---

## 1. 査定結果サマリー

| タスク | 判定 | 詳細 |
| :--- | :--- | :--- |
| TBD「うねり版」統計力学の数式化 | ✅ 合格 | 構造的に整合、v15.0との接続明示 |
| 重力との二重構造の整合性確認 | ✅ 合格 | Ψ場の重ね合わせとして一貫 |
| スケール係数 Ξ の導出 | ⚠️ 条件付き合格 | 次元が合わない — 要確認 |

---

## 2. 合格: `Temporal_Undulation_Formalism.md`

### 良い点

- **v15.0との接続**: `Δt ∝ ΔS/I` からの Ψ場への拡張は自然で説明が丁寧
- **用語の統一**: 「定常摂動 (Stationary Perturbations)」を一貫して使用、電磁波との混同を回避している
- **Langevin方程式の導入**: TBDの拡張として `η dx/dt = -∇Ψ + √(2D)ξ(t)` は統計力学として形式的に正しい構造
- **二重構造の明示**: 局所（重力、1/r）と大域（DM、ln(r)）の分離が Section 4.2-4.3 で明確に記述されている
- **フラット回転曲線の導出方針**: Section 4.2 で `ρ_tens ∝ r⁻²` → `M(r) ∝ r` → `v = const` の論理が示されている

### 1点の懸念（軽微）

Section 3.1 の Langevin 方程式は**test particle の運動方程式**として書かれているが、Ψ 自体が「時間流速の密度」なら Ψ の次元と勾配の次元の整合が必要。Phase 2 で形式化を進める際に確認すること。これは現時点のドラフトとしては許容範囲。

---

## 3. 条件付き合格: スケール係数 Ξ の次元問題

`galactic_profile.py` の以下の実装を確認した:

```python
self.N_leech = 196560  # Coordination Number (dimensionless)
self.kappa = np.pi / 24.0  # dimensionless
scaling_factor = (self.N_leech / self.kappa) * (4.0 * np.pi)  # dimensionless
rho_ksau = scaling_factor * (1.0 / alpha)   # dimensionless × dimensionless = dimensionless
M_tens = 4 * np.pi * rho_ksau * (r - r_c * np.arctan(r/r_c))  # [Msun/kpc] × [kpc] ???
```

**問題**: `rho_ksau` は無次元数として計算されているが、直後の `M_tens` の計算では `rho_ksau` が `[Msun/kpc²]` の次元を持つ密度として使われている（pseudo-isothermal の `M(r) = 4π ρ₀ r_c² (r - r_c arctan(r/r_c))` の形式から見て）。

`Temporal_Undulation_Formalism.md` Section 4.1 では Ξ を「ブリッジ係数」として定義しているが、その物理次元が記述されていない。N=196560 は無次元の配位数、κ は無次元の結合定数——これらの比は無次元であり、銀河スケールの密度 [Msun/kpc³] との接続に**単位変換の根拠**が必要。

現在の MAE=7.13 km/s は数値的に出ているが、それは単位系の不整合を数値が「吸収」している可能性がある。

**アクション（Phase 2 着手前に必須）:**
- `Temporal_Undulation_Formalism.md` Section 4.1 に Ξ の**物理次元を明記**する
- `galactic_profile.py` の `rho_ksau` の次元が何であるかをコメントに記載する
- 単位変換の根拠（例: Planck単位との対応、または自然単位系の定義）を示す

---

## 4. MOND への言及について

Section 4.3 の末尾:

> "This dual structure eliminates the need for 'modified gravity' (MOND)"

この文は現時点では**過剰主張**。MOND を否定するには少なくとも MOND が説明する現象（Tully-Fisher 関係など）を KSAU v17.0 が同等以上の精度で再現することを示す必要がある。現段階では「MOND と同じ現象（フラット回転曲線）を異なるメカニズムで説明しようとしている」が正確。**この文は削除または「MOND的修正を必要としない可能性を示す」に弱めること。**

---

## 5. Phase 1 全体の最終評価

Phase 1 の5タスク全完了を確認した。ロードマップのチェックマークを以下の通り承認する:

| タスク | 承認 |
| :--- | :--- |
| T_μν の定義（新規仮定として整理） | ✅ |
| κ依存の組み込み | ✅ |
| 銀河回転曲線との定量比較（MAE=7.13 km/s） | ✅ ただし次元問題を Phase 2 前に解決 |
| TBD「うねり版」数式化 | ✅ |
| 二重構造の整合性確認 | ✅ |

**Phase 2 への移行を条件付きで承認する。**

条件: `Ξ の物理次元の明記` と `MOND への言及の修正` を Phase 2 の最初のタスクに追加すること。

---

## 6. Phase 2 タスクへの補足

- **Unraveling Operator Ｕ(t)**: Jones多項式のスケーリングは解析的に困難な場合が多い。「Jones多項式の特定のリミット（高温展開など）でのスケーリング」に絞ることを推奨する。
- **GUTスケールギャップ**: 10¹⁶ GeV vs 4.64×10¹⁴ GeV の因子〜22 をどう扱うか。「有効質量の変化」としての説明は定性的には許容するが、定量的な導出なしに「整合」とは言わないこと。

お疲れ様でした。Phase 1b の完成度は高い。

---
*Auditor: Claude Sonnet 4.5 | 2026-02-17*
