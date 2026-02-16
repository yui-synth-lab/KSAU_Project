# KSAU v2.3 Roadmap: Response to Critical Review

**Date:** February 5, 2026
**Status:** Planning / Pre-computation

## 1. Addressing Systematic Mass Deviation
**Status:** ✅ Preliminary Verification Complete
**Finding:** Adding `Signature` (Sig) and `Total Linking Number` ($L_{tot}$) significantly improves heavy quark predictions.
- **Top Error:** +107% (v2.2) $\to$ +54% (v2.3 Preview)
- **Bottom Error:** -61% (v2.2) $\to$ -15% (v2.3 Preview)
- **$R^2$:** 0.951 $\to$ 0.963

**Action Items:**
- [ ] **Data Augmentation:** Calculate `Writhe` number for all candidates (requires knot projection software/library).
- [ ] **Generation-Dependent Coefficients:** Test model $\ln(m) = \alpha \cdot Vol + C_{gen}$ where $C_{gen}$ depends on generation index (1, 2, 3).
- [ ] **Refine Light Quark Model:** Down/Strange errors increased in the linear model. Investigate "Zero-Anchor Stability" for light quarks.

## 2. Link Selection Protocol (Transparency)
**Critique:** "Why L6a5?" is undefined.
**Action Items:**
- [ ] **Create Candidate Database:** `data/all_prime_links_up_to_10crossings.csv` with calculated Vol, Sig, and Color components.
- [ ] **Define Selection Algorithm:**
  1.  Filter by Component Number ($N=3$).
  2.  Sort by Hyperbolic Volume.
  3.  Match Color Charge symmetry ($SU(3)$ representations).
  4.  Select lowest complexity link matching mass scale.

## 3. Mathematical Rigor (SU(3) $\to$ T³)
**Critique:** Lack of proof for Abelian Dominance.
**Action Items:**
- [ ] **Literature Review:** Cite "Abelian Dominance in QCD" (Ezawa, Iwazaki, etc.) and "Monopole Condensation".
- [ ] **Numerical Proof (Scope for v3.0):** Lattice QCD simulation comparison (High effort). For v2.3, provide theoretical justification via Wilson loops.

## 4. Experimental Predictions
**Critique:** Predictions are too vague.
**Action Items:**
- [ ] **Calculate $V_{ub}$:** Refine the "Cubic Generation Barrier" model to output precise number (Target: $0.0036 \pm 0.0001$).
- [ ] **Spin Correlation ($t \to bW$):**
  - SM: $C = -0.41$
  - KSAU: $C = -0.41 + \delta_{topo}$ (where $\delta_{topo} \propto \t\text{Signature}(L_{top})$).
  - Calculate magnitude of $\delta_{topo}$.

## 5. Conceptual Unification
- **Higgs Connection:** Propose that Hyperbolic Volume determines the *effective* Yukawa coupling $y_f$, not the VEV.
- **3 Generations:** Link to "Three-Manifold Mutation" or "Braid Group $B_3$" structure.
