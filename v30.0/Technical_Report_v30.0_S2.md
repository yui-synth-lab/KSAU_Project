# Technical Report v30.0 Section 2: Chern-Simons Duality and S-Dual Mass Formula

**Status:** EXPLORATORY-SIGNIFICANT (Session 10 — Multiple Comparison Addressed) | Bonferroni RESOLVED (Session 13)
**Date:** 2026-02-20 (Updated: 2026-02-20 Session 13)
**Authors:** KSAU Simulation Kernel (Gemini CLI)
**Auditor:** Claude (Independent Audit)

> **Classification note (Session 10):** The statistical result p = 0.0078 (k near 24/25) is
> **EXPLORATORY-SIGNIFICANT**: it is stable across k-grid resolutions and p < 0.05, but does not
> pass conservative Bonferroni correction (α = 0.005). The target k = 25 has pre-registered
> theoretical motivation (SU(24) shifted level), which moves this result toward the confirmatory
> end of the spectrum, but absent a formal pre-registration record the conservative
> "exploratory" label is retained. Upgrading to CONFIRMATORY requires either (a) formal
> pre-registration evidence or (b) an independent replication on a distinct dataset.

> **Session 13 Update — Bonferroni Decision and WZW Calculation:**
> Task H-1 (Bonferroni 決着) および Task C-1 (WZW level-k 計算) が完了。
> (1) Bonferroni 問題: 保守的 α=0.0050 未達を「**明示的格下げ確定**」とし、宙吊り状態を解消（§4.2 更新）。
> (2) WZW 計算: $E_{vac} = 7\pi/k$ は標準 WZW 理論から **導出不可能** と判明。
> Condition E ($q_{mult}=7$ の代数的起源) および Section 3 WZW 証明の要求は
> 「現状の数学的枠組みでは証明不能」として正式クローズ（§7 参照）。

---

## 1. The Duality Hypothesis

This report addresses the "k-reversal problem" (問い A). We propose that the KSAU mass formula

$$\ln(m) \propto \frac{\pi}{k} \cdot N \cdot V + C$$

is S-dual to the Chern-Simons partition function at level $k$.

---

## 2. Level Scan Results (`cs_level_scan.py`, Session 8)

### 2.1 Best-fit k

| Rank | k value | Total Err | R² (quarks) | R² (leptons) | R² (combined) |
|------|---------|-----------|-------------|--------------|---------------|
| 1    | 25.100  | 15.4311   | 0.8343      | 0.9706       | 0.8403        |
| 2    | 25.000  | 15.4350   | 0.8340      | 0.9765       | 0.8402        |
| 3    | 25.200  | 15.4634   | 0.8343      | 0.9640       | 0.8399        |

- **Optimal k-level:** $k \approx 25.06$ (refined at Δk=0.01; see §4.1 sensitivity analysis)
- **Theoretical Target:** $k = 25$ (corresponding to $SU(24)$ level-1 WZW with $h = 24$: $k_{\text{shifted}} = k + h = 1 + 24 = 25$)
- **R² (combined, 8 fermions):** $0.8403$ — moderate explanatory power; not a near-perfect fit.

### 2.2 Twist Factor Definition and Physical Interpretation (Session 10 — Issue 4 Resolution)

The twist factor entering the mass formula for each quark $q$ is:

$$\tau_q = \left(2 - g_q\right) \times (-1)^{c_q}$$

where $g_q \in \{1, 2, 3\}$ is the quark generation and $c_q$ is the number of topological
components of the associated topology slot (loaded from `topology_assignments.json`).

**Physical interpretation:**

- **Generation factor $(2 - g_q)$:** Encodes the generation-dependent coupling strength in the
  KSAU dimensional reduction. For $g_q = 1$ (1st generation: up, down) the factor is $+1$;
  for $g_q = 2$ (charm, strange) the factor is $0$ (the 2nd-generation slot sits at a twist
  node, i.e., it is twist-neutral); for $g_q = 3$ (top, bottom) the factor is $-1$ (anti-twist).
  This pattern reflects a $\mathbb{Z}_3$ symmetry of the generation space projected onto $\mathbb{Z}$.

- **Component sign $(-1)^{c_q}$:** Each topology slot has an intrinsic orientation determined
  by whether it contains an even or odd number of topological components. This factor is a
  discrete topological invariant of the slot, not of the particle: it is topologically conjugate
  to the winding parity of the associated 3-cycle.

**Caveat:** The above is a candidate physical interpretation consistent with the KSAU
dimensional-reduction framework. The generation factor $(2 - g)$ specifically has not been
derived from first principles in the current session; it is recorded as a **phenomenological
ansatz** that reproduces the correct mass hierarchy structure. Derivation from the geometry of
the Leech lattice or a WZW representation-theoretic argument is an open task.

### 2.3 Intercept Formula: Candidate Interpretation (Issue 2 / Condition B Resolution)

The k-dependent intercept used in the scan is:

$$b_q(k) = -q_{\text{mult}} \left(1 + \frac{\pi}{k}\right)$$

where $q_{\text{mult}} = 7.0$ is loaded from SSoT (`cosmological_constants.json →
scaling_factors → quark_mass_intercept_multiplier`). **$q_{\text{mult}} = 7$ is a fitted
free parameter whose algebraic origin has not been derived** (see §2.4).

**Motivation of the functional form (candidate):**

The functional form $b_q(k) = -q_{\text{mult}}(1 + \pi/k)$ arises naturally if one treats
the intercept as a classical piece ($-q_{\text{mult}}$) plus a quantum correction proportional
to $\kappa = \pi/k$. In a CS/WZW-type theory the ground-state correction is of order
$h^{\vee}/(k + h^{\vee})$. For large $k$ this reduces to $h^{\vee}/k$.

> ⚠️ **Unverified approximation (Session 10 fix — Issue 2):**
> Prior versions of this report stated this correction uses "$h \approx \pi$ as the effective
> dual Coxeter number in the KSAU dimensional reduction." This is **incorrect notation** and
> has been removed. The standard dual Coxeter number of $SU(24)$ is $h^{\vee}(SU(24)) = 24$,
> not $\pi$. The functional form $\pi/k$ arises because $\kappa \equiv \pi/k$ is the KSAU
> kinematic parameter (angle per level), and in this framework $\kappa$ plays the role of
> the coupling — not because $h^{\vee} = \pi$.
>
> The statement "$h \approx \pi$" was a notational error and has been retracted. The intercept
> formula is phenomenologically motivated (the $\pi/k$ dependence matches the kinematic
> parameter $\kappa$) but is **not a rigorous derivation** from CS/WZW theory.
> It is recorded as a **candidate functional form**, not a derivation.

### 2.4 Free Parameter Transparency (Issue 3 / Condition C — Session 10)

| Parameter | Value | Source | Status |
|-----------|-------|--------|--------|
| $q_{\text{mult}}$ | 7.0 | SSoT (`cosmological_constants.json`) | **Free parameter — algebraic origin unknown** |
| $N_q$ (quark multiplicity) | from JSON | SSoT | Phenomenological |
| $N_l$ (lepton multiplicity) | from JSON | SSoT | Phenomenological |
| $C_l$ | $\ln(m_e)$ | Physical (electron mass anchor) | Derived |

**$q_{\text{mult}} = 7$ is a free parameter fitted to the quark mass spectrum.** Its value
is stored in the SSoT JSON, but its algebraic derivation from the geometry of the Leech
lattice, the E8×E8 root system, or any other KSAU theoretical structure has not been
established. This means the reported R² = 0.84 benefits from a degree of freedom whose
justification is currently circular (fit to data, stored as "constant").

This fact does **not** invalidate the MC significance test (which tests the volume *pairing*
structure under fixed formula parameters), but it limits the interpretive strength of the
R² value as evidence for the CS duality hypothesis.

**Open task (Condition C):** Derive $q_{\text{mult}} = 7$ from first principles, or demonstrate
that no such derivation exists and reclassify it explicitly as a fitted nuisance parameter.

---

## 3. Monte Carlo Significance Test — FULL HISTORY

### 3.1 Implementation History

| Session | MC Design | p value | Status |
|---------|-----------|---------|--------|
| 7 | Sorted random masses (H0 contaminated) | 0.14 | REJECTED |
| 8 | Volume permutation; q_vol / q_twist shuffled **independently** | 0.0067 | ACCEPTED (Condition A flagged) |
| 9 | Volume permutation; q_vol + q_twist shuffled with **shared index** | 0.0078 | Condition A fixed |
| 10 | Session 9 design + multiple comparison analysis + resolution sensitivity | 0.0078 | **EXPLORATORY-SIGNIFICANT** |

### 3.2 Current Implementation (Session 9, unchanged)

A single permutation index array `perm_q` is drawn once per trial:

```python
perm_q       = rng.permutation(len(all_q_vols))
q_vol_rand   = all_q_vols[perm_q]    # same index
q_twist_rand = q_twist_obs[perm_q]   # same index — coherent (vol, twist) pair
l_vol_rand   = rng.permutation(all_l_vols)   # leptons: no twist factor
```

### 3.3 Null Hypothesis

> $H_0$: The physical assignment of quark (volume, twist) topology slot-pairs to quark masses
> is no more special than a random permutation of those slot-pairs.

Under $H_0$, observed mass values are **held fixed**; the 6-element array of (volume, twist)
pairs is permuted as a unit ($6! = 720$ possible permutations).

### 3.4 Results (10,000 trials, seed=42)

| Metric | Value |
|--------|-------|
| Observed best-fit k | 25.06 (Δk=0.01) / 25.10 (Δk=0.10) |
| P(random shuffle → k near 24 or 25, ±0.25) | 0.0078 (78/10000) |
| Significance threshold α | 0.05 |
| Bonferroni-corrected α (conservative) | 0.0050 |
| **Verdict (raw p < 0.05)** | PASSED |
| **Verdict (Bonferroni)** | NOT PASSED (p=0.0078 > 0.0050) |
| **Overall classification** | **EXPLORATORY-SIGNIFICANT** |

---

## 4. Sensitivity and Multiple Comparison Analysis (`cs_sensitivity_analysis.py`, Session 10)

### 4.1 k_range Resolution Sensitivity (Issue 5 Resolution)

| Resolution | N points | k_obs | p(k near 24/25) | hits |
|-----------|---------|-------|----------------|------|
| Δk = 0.10 | 401 | 25.1000 | 0.0078 | 78/10000 |
| Δk = 0.05 | 801 | 25.0500 | 0.0048 | 48/10000 |
| Δk = 0.02 | 2001 | 25.0600 | 0.0078 | 78/10000 |
| Δk = 0.01 | 4001 | 25.0600 | 0.0071 | 71/10000 |

**Finding:** k_obs is stable at 25.05–25.10 across all resolutions. p values range
0.0048–0.0078, all remaining below 0.05. The k = 25.1 result is **not a discretization
artifact** of the Δk = 0.10 grid.

### 4.2 Multiple Comparison Analysis (Issue 1 Resolution)

**Window analysis:**

The target window $|k - 24| < 0.25$ or $|k - 25| < 0.25$ spans approximately **2.45% of
the k_range** [10, 50]. Under a uniform-random-k null this would give P(hit) ≈ 0.0245.
The observed MC p = 0.0078 is **3.1× smaller** than this baseline, showing that the physical
(volume, twist) assignment concentrates best-fit k into the Niemeier window substantially
more than random topology assignments do.

**Bonferroni analysis:**

| Quantity | Value |
|---------|-------|
| Points in Niemeier window (Δk=0.1 grid) | 10 |
| Conservative Bonferroni α = 0.05 / 10 | 0.0050 |
| Observed p | 0.0078 |
| Bonferroni result | **FAIL** (p > 0.0050) |

**Why denominator = 10, not 401 (Condition D — Session 11):**

The MC test does **not** perform 401 independent hypothesis tests (one per grid point).
It performs a **single binary test**: does the best-fit k land inside the pre-specified
Niemeier window $|k-24|<0.25$ or $|k-25|<0.25$, or not? The 401 grid points are merely
the resolution of the optimisation; they are not 401 separate hypotheses.

The Bonferroni denominator is therefore the number of *distinct target windows* being tested,
not the number of grid points. Since only one window is specified (the union of the two
half-width-0.25 intervals around k=24 and k=25), the correction would strictly be
α/1 = 0.05 — no correction needed. Using denominator 10 (the number of grid points that
fall inside the window) is a **conservative over-correction**: it assumes each in-window
grid point constitutes an independent sub-hypothesis, which is more conservative than
the single-window interpretation. The result p=0.0078 fails even this conservative
threshold, making the EXPLORATORY-SIGNIFICANT classification maximally conservative.

Under the correct single-window interpretation, with the pre-registered target k=25
(motivated by SU(24) theory before the scan), the result p=0.0078 < 0.05 would restore
the PASSED verdict without any multiple-comparison penalty.

**Pre-registration status:**

The target $k = 25$ has theoretical motivation that predates the numerical scan:
$k_{\text{shifted}} = k + h^{\vee}(SU(24)) = 1 + 24 = 25$ (KSAU framework, Section 2 theory).
This constitutes a **theoretical pre-registration**, though not a formal statistical one.
Under the pre-registration argument, the multiple comparison correction is not required
(there is effectively one hypothesis being tested), which would restore the PASSED verdict.

**Final classification:** The theoretical pre-registration is real but informally documented.
The conservative classification is **EXPLORATORY-SIGNIFICANT**, pending either:
(a) formal documentation of the pre-registration, or
(b) independent replication.

---

## 5. Physical Interpretation

The value $k \approx 25$ aligns with the shifted level of an $SU(24)$ theory:

$$k_{\text{shifted}} = k + h^{\vee} = 1 + 24 = 25$$

where $h^{\vee}(SU(24)) = 24$ is the standard dual Coxeter number (not $\pi$; the earlier
notation error has been corrected in §2.3). This suggests the mass spectrum may be generated
by a level-1 WZW model on the 24-dimensional bulk boundary.

---

## 6. Conclusion

| Item | S7 | S8 | S9 | S10 | S11 | **S13** |
|------|----|----|----|----|-----|---------|
| MC null hypothesis | Contaminated | Volume perm (indep. shuffle) | Volume perm (shared index) | Same as S9 | Same as S9 | ✅ unchanged |
| p-value (k near 24/25) | 0.14 | 0.0067 | 0.0078 | 0.0078 | 0.0078 | 0.0078 |
| Bonferroni analysis | — | — | — | p=0.0078 > α=0.0050 (FAIL) | ✅ Denominator rationale added | ✅ **RESOLVED: α=0.005 未達を明示確定** |
| Resolution stability | — | — | — | ✅ stable (dk=0.10→0.01) | ✅ unchanged | ✅ unchanged |
| MC index coherence | — | ❌ | ✅ | ✅ | ✅ | ✅ unchanged |
| h ≈ π notation | — | Error present | Error present | ✅ Retracted | ✅ unchanged | ✅ unchanged |
| q_mult=7 status | Free param | Free param | Free param | ✅ Explicitly flagged | ✅ unchanged | ✅ **WZW 導出不能と確定（§7）** |
| q_twist definition | Undocumented | Undocumented | Undocumented | ✅ Documented (§2.2) | ✅ unchanged | ✅ unchanged |
| **Overall status** | Candidate | Statistically Sig. | Statistically Sig. | EXPLORATORY-SIGNIFICANT | EXPLORATORY-SIGNIFICANT | **EXPLORATORY-SIGNIFICANT (Final)** |

**Summary (Session 13 Final):** Section 2 is classified as **EXPLORATORY-SIGNIFICANT (Final)**. Two tasks are now resolved:

1. **Bonferroni 決着（Task H-1）**: 保守的 Bonferroni 閾値 α=0.0050 に対し p=0.0078 は未達である。これを「明示的格下げ確定」とし、境界線上の宙吊り状態を解消する。主張の最終形: "p < 0.05 は成立するが、保守的 Bonferroni 補正後は有意ではない。単一窓事前登録を仮定した場合のみ PASSED となる。" これ以上の宙吊りは認めない。

2. **WZW 導出不能の確定（Task C-1 派生）**: $b_q(k)$ の関数形 $-7(1+\pi/k)$ は、標準 WZW 理論から第一原理的に導出不可能であると判明（§7 参照）。Condition E ($q_{mult}=7$ の代数的起源) の WZW 経路はクローズ。

**現在の解釈:** Section 2 は実証的に意味のある探索的結果（p < 0.05 安定、3.1× 超過）であるが、理論的根拠（CS/WZW 双対性）は現時点では候補解釈の域を出ない。

**Outstanding tasks (更新):**
- Algebraic derivation of $q_{\text{mult}} = 7$: WZW 経路は閉鎖。別の代数的枠組み（E₈ 根系、Leech 格子等）が存在する場合のみ再開
- CS 双対性の第一原理証明: OPEN（非標準 WZW/curved background の可能性は未調査）

---

## 7. WZW Level-k 計算結果（Session 13 NEW — Task C-1）

### 7.1 解析的計算の結論

$SU(N)$ WZW モデル（level $k$）における正確な真空エネルギーは：

$$E_0(SU(N), k) = -\frac{c}{24} = -\frac{N^2-1}{24} \cdot \frac{k}{k+N}$$

大 $k$ 展開（$k \gg N$ の仮定が必要）：

$$E_0 \approx -\frac{N^2-1}{24} + \frac{N(N^2-1)}{24k} + O(k^{-2})$$

### 7.2 KSAU 公式との比較

KSAU の要求: $E_{vac} = 7\pi/k$ つまり、$1/k$ の係数 $= 7\pi \approx 21.99$

WZW 理論の結果: $1/k$ の係数 $= N(N^2-1)/24$（整数値）

| $N$ | $N(N^2-1)/24$ | $7\pi$ との差 |
|-----|--------------|--------------|
| 7 | 14 | $-7.99$ |
| 8 | 21 | $-0.99$ |
| 9 | 30 | $+8.01$ |
| 13 | 91 | $+69.0$ |
| 24 | 575 | $+553$ |

整数 $N$ で $N(N^2-1)/24 = 7\pi$ を満たすものは存在しない（$7\pi$ は無理数）。

### 7.3 $\pi$ が分子に現れない理由

WZW 理論において、中心電荷 $c = k(N^2-1)/(k+N)$ は $N, k$ の有理関数である（Sugawara 構成）。したがって $c/24$ は有理的であり、$\pi$ は独立な係数として現れえない。$\pi$ が WZW 計算に現れるのはモジュラー変換や経路積分（曲った背景上）においてのみであり、平坦空間ハミルトニアンの固有値には現れない。

### 7.4 $SU(13)$ との偶発的な一致

$SU(13)$ では古典項 $-(N^2-1)/24 = -168/24 = -7$ が KSAU の古典項 $-7$ と一致する。しかし量子補正の係数 $N(N^2-1)/24 = 91$ は $7\pi \approx 21.99$ と大きく異なる（比 $\approx 4.14$）。これは偶然の数値的一致であり、理論的根拠はない。

### 7.5 最終判定

**$E_{vac} = 7 \cdot (\pi/k)$ は標準 WZW 理論から導出不可能。**

根拠:
1. $c(SU(N),k)$ は $N, k$ の有理関数 → $\pi$ は独立係数として出現不能
2. $h^\vee$ は常に正整数 → $h^\vee = \pi$ は不成立
3. 大 $k$ 展開の係数は整数値 → $7\pi$ と等しい整数 $N$ は存在しない
4. $k=25$, $N=24$ では展開パラメータ $N/k \approx 0.96 \approx 1$ であり、大 $k$ 展開そのものが無効

**Condition E のステータス（更新）:** `CLOSED — WZW 経路不成立確定`。

$q_{mult} = 7$ の代数的起源を WZW 真空エネルギーに求める経路は閉鎖する。代替として、Leech 格子 $N_{Leech}$ の素因数 7 との接続（Section 3）が現在唯一の代数的動機付けとして残る。

> **注意:** 非標準構成（曲った背景の WZW、コセット理論、非コンパクト WZW）では状況が異なる可能性がある。これらは未調査の open question として記録する。

---
*KSAU v30.0 Technical Report S2 — Status: EXPLORATORY-SIGNIFICANT (Final, Session 13)*
*Auditor: Claude (Independent Audit) — 2026-02-20*
*Session 13: Task H-1 (Bonferroni 決着) + Task C-1 (WZW 計算) 完了*
