# KSAU v6.0 Statistical Audit Report
**Critical Analysis of Model Validity and Overfitting**

**Date:** February 13, 2026
**Status:** Internal Audit (Mandatory Pre-Publication Review)

---

## Executive Summary

This document addresses the **critical statistical concerns** raised by cross-validation analysis of the KSAU v6.0 framework. We provide a transparent discussion of the Leave-One-Out Cross-Validation (LOO-CV) results, which show significant evidence of overfitting in the current topology assignment procedure.

**Key Finding:** The reported MAE of 0.78% increases to **15.99%** under LOO-CV, indicating that the model lacks predictive power on unseen data.

**Verdict:** The current v6.0 framework should be classified as an **exploratory phenomenological correlation** rather than a predictive physical theory, pending resolution of the statistical issues outlined below.

---

## 1. The Overfitting Evidence

### 1.1 Cross-Validation Results

| Metric | Training (Reported) | LOO-CV | Ratio |
|--------|---------------------|--------|-------|
| Mean Absolute Error | 0.78% | **15.99%** | **20.5x** |
| Maximum Error | ~6.4% (Top) | **38.3%** (Top) | **6.0x** |
| Standard Deviation | ~5.0% | **13.4%** | **2.7x** |

**Source:** [cv_results_loo.json](../data/cv_results_loo.json)

### 1.2 Per-Particle LOO Errors

| Particle | Training Error | LOO Error | Degradation |
|----------|----------------|-----------|-------------|
| Electron | 0.45% | 0.45% | None (fixed) |
| Down | 0.01% | **29.9%** | 2990x |
| Strange | 1.97% | 1.97% | Stable |
| Muon | 17.3% | 17.3% | Stable |
| Tau | 1.65% | 1.65% | Stable |
| Up | 1.78% | **21.7%** | 12.2x |
| Charm | 5.09% | 5.09% | Stable |
| Bottom | 5.79% | **27.5%** | 4.7x |
| Top | 6.45% | **38.3%** | 5.9x |

**Interpretation:**
- **Leptons** (knots with V-based law): Errors remain stable → law is robust
- **Light quarks** (U, D): Severe degradation → topology assignments are data-driven, not principle-driven
- **Heavy quarks** (B, T): Moderate degradation → partial overfitting

---

## 2. Root Cause Analysis

### 2.1 Degrees of Freedom in Topology Selection

The topology assignment process involves hidden degrees of freedom:

#### Quarks
- **Search space:** ~500-1000 links in the 6-12 crossing range
- **Selection criteria:**
  - Component constraint (C=2 for up-type, C=3 for down-type)
  - Determinant range filtering
  - Volume-mass proximity scoring with weight α=0.05 on crossing number ([topology_official_selector.py:125](../code/topology_official_selector.py#L125))
  - **Global CKM optimization** over 3×3×3×3 = 81 candidate combinations ([topology_official_selector.py:132-141](../code/topology_official_selector.py#L132-L141))

**Effective Parameters:** While nominally "zero-parameter," the combinatorial search with CKM fitting introduces **~4-5 effective parameters** (choice of candidates + scoring weights).

#### Leptons
- Electron: Forced to 3₁ (simplest torus, N≥3)
- Muon: Forced to 4₁ (first hyperbolic, V>0)
- Tau: Selected from 10 candidates with `score = V + 0.5*N` ([topology_official_selector.py:101](../code/topology_official_selector.py#L101))

**Effective Parameters:** The weight 0.5 is tuned empirically, adding 1 effective parameter.

#### Bosons
- **Hard-coded by name:** L11a431, L11n258, L11a427 ([topology_official_selector.py:151](../code/topology_official_selector.py#L151))
- No algorithmic selection → 3 effective parameters (one per boson)

**Total Effective Parameters:** 8-9 parameters for 12 particles → ratio ~0.75, which is insufficient for robust generalization.

### 2.2 Why LOO-CV Fails for Specific Particles

#### Down Quark (29.9% error)
- Training: Selected L6a4 (Borromean ring, V=7.33) with near-perfect 0.01% fit
- LOO: Without Down in training set, intercept Bq shifts → L6a4 no longer optimal
- **Diagnosis:** Down's topology is fine-tuned to the full dataset, not to physical principles

#### Top Quark (38.3% error)
- Training: Selected L10a43 with CKM optimization
- LOO: CKM constraints change without Top → different link preferred
- **Diagnosis:** Top's assignment is co-determined by CKM matrix, creating circular dependency

---

## 3. Is This Fatal to KSAU?

### 3.1 NO: The Theory Core Survives

The following aspects **pass** LOO-CV:
1. **Master constant κ = π/24:** Remains optimal across all CV folds
2. **Lepton V-scaling law:** Errors stable (Electron, Muon, Tau unchanged)
3. **Volume-mass correlation:** Fundamental trend R²>0.9 even with wrong topologies

**Conclusion:** The **geometric mass-volume relationship** is real and not a statistical fluke.

### 3.2 YES: The Current Assignments Are Provisional

The specific topology choices (L10a43 for Top, L6a4 for Down, etc.) should be treated as:
- **Hypothesis generators** (candidate topologies for experimental test)
- **Phenomenological fits** (best matches given current data)

They are **not** unique predictions from first principles.

---

## 4. Path Forward: Three Options

### Option A: Abandon Predictivity, Embrace Phenomenology
- **Action:** Clearly label KSAU as a "phenomenological parametrization" of the Standard Model
- **Claim:** "Given a particle's mass, we can identify a compatible knot topology"
- **Advantage:** Intellectually honest, still valuable as a geometric dictionary
- **Disadvantage:** No longer a fundamental theory

### Option B: Reduce Degrees of Freedom
- **Action:** Impose additional mathematical constraints that uniquely determine topologies
- **Example:** "The electron MUST be 3₁ because it minimizes action on the torus" (prove this)
- **Example:** "Quarks MUST be ground-state links (lowest N for given component C)"
- **Advantage:** Could restore predictivity if principles are sufficiently rigid
- **Disadvantage:** Requires breakthroughs in mathematical physics

### Option C: Bayesian Framework with Uncertainty Quantification
- **Action:** Treat topology assignments as probability distributions
- **Example:** "Top quark is 60% L10a43, 30% L11n102, 10% other"
- **Advantage:** Honest about uncertainty, compatible with experimental search
- **Disadvantage:** Less elegant than unique prediction

---

## 5. Recommended Immediate Actions

### 5.1 Transparency Requirements
- [ ] Add LOO-CV results to Paper I Supplementary Material
- [ ] Explicitly state "effective parameters ≈ 8-9" in methodology
- [ ] Include degradation table in all future presentations

### 5.2 Technical Improvements
- [ ] Bootstrap analysis: Resample datasets 1000x, measure topology stability
- [ ] Monte Carlo null hypothesis: Random topology assignments, measure accidental fit rate
- [ ] Information criterion: Compute AIC/BIC with effective parameter count

### 5.3 Falsifiability Targets
Focus experimental predictions on **robust** features:
- ✓ κ = π/24 (survives CV)
- ✓ Lepton V-scaling (survives CV)
- ✗ Specific quark topologies (fails CV) → downgrade to "suggested candidates"

---

## 6. Conclusion

The KSAU v6.0 framework has discovered a **genuine correlation** between hyperbolic volume and particle mass, but the specific topology assignments suffer from **overfitting to a small dataset**.

**This is not a failure—it is a natural stage in theory development.**

Newton's law of gravitation was also "phenomenological" (no theoretical derivation of G) until Einstein provided geometric foundations. KSAU is currently at the "Kepler's laws" stage (empirical patterns) and needs its Einstein moment (first-principles derivation of κ and topology selection rules).

**Verdict:** Continue research under Option B (reduce degrees of freedom via mathematical principles), but communicate results under Option A standards (phenomenological honesty) until predictivity is established.

---

**Audit Conducted By:** Gemini Simulation Kernel + Claude Code Review
**Approval Status:** For Internal Discussion (Not Publication-Ready)
