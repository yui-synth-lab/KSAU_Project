# KSAU v16.1 Publication Checklist

**Date Created:** 2026-02-17
**Review Status:** Internal Audit COMPLETED (AI Consistency Check)
**Target Submission:** Physical Review D / JHEP / Communications in Mathematical Physics

---

## Pre-Submission Checklist

### 1. Technical Content Revisions

#### A. Energy Scale Specification ✅ DONE (Gemini, 2026-02-17)
- [x] Add explicit statement for α = κ/18 energy scale
- [x] Add explicit statement for α_s = 0.90κ energy scale
- [x] Clarify "geometric anchor" vs "experimental measurement" distinction
- [x] Add Section 4.3 "Renormalization Group Mapping" to `KSAU_v16_Newtonian_Transition.md`

#### B. CKM Suppressed Transitions ✅ DONE (Gemini, 2026-02-17)
- [x] Add subsection in Limitations (Section 5)
- [x] Acknowledge errors in V_ub, V_td, V_ts
- [x] Explain why volume alone is insufficient
- [x] Propose higher-order topological invariants as solution

#### C. Dark Matter Spectrum Update — RECOMMENDED
- [ ] Update dark matter candidate table
- [ ] Remove 511 keV candidate (already retracted in v16.1)
- [ ] Clarify status of remaining candidates (N=6, N=2)
- [ ] Add observational alignment discussion

---

### 2. Mathematical Rigor

#### D. 24D→4D Projection Formalism — RECOMMENDED
- [ ] Add mathematical appendix defining projection operator
- [ ] Justify why K_24 - K_4 represents "information loss"
- [ ] Derive dilution factor from spectral geometry
- [ ] Prove or cite N=41 as unique global minimum

#### E. Impedance Law Microscopic Derivation ✅ DONE (Gemini, 2026-02-17)
- [x] Add explicit statement that v₀ = 1/(1+κρ) remains a macroscopic limit
- [x] Propose microscopic derivation as future work
- [x] Compare to Newton→Einstein analogy

---

### 3. Visualization & Presentation

#### F. Figures & Diagrams ✅ PARTIAL (Gemini, 2026-02-17)
- [x] **Figure 2:** N=41 modular action minimization plot — embedded
- [x] **Figure 3:** Scaling Law comparison (Exp vs Rational) — embedded
- [x] **Figure 4:** Density components bar chart — embedded
- [ ] **Figure 1:** 24D→4D projection schematic
- [ ] **Figure 5:** Dark matter spectral hierarchy

#### G. Equation Numbering ✅ DONE (Gemini, 2026-02-17)
- [x] Number all key equations (Eq. 1, 2, 3)
- [x] Verified consistency in `KSAU_v16_Newtonian_Transition.md`

---

### 4. Documentation & Reproducibility

#### H. References & Citations ✅ DONE (Gemini, 2026-02-17)
- [x] Complete bibliography added (9 references)
- [x] Cite Diamond & Shurman (2005) for modular index
- [x] Acknowledge Gemini/Claude co-authorship

#### I. Code & Data Availability ✅ DONE (Gemini, 2026-02-17)
- [x] Figure generation scripts created
- [x] Monte Carlo null test & Sensitivity scripts created
- [x] All scripts verified and producing consistent p-values (p ≈ 0.012)

#### J. Supplementary Materials ✅ DONE (Gemini, 2026-02-17)
- [x] Monte Carlo null hypothesis test (`Monte_Carlo_Null_Test.py`)
- [x] Monte Carlo sensitivity analysis (`Monte_Carlo_Sensitivity_Analysis.py`)

---

### 5. Writing Quality

#### K. Language & Style ✅ DONE (Claude + Gemini, 2026-02-17)
- [x] Proofread for grammar/typos
- [x] Ensure honest reporting of p-value results (Target p<0.001 not met, but p<0.05 confirmed)

#### L. Clarity & Accessibility ✅ DONE (Gemini, 2026-02-17)
- [x] Add glossary of terms
- [x] Simplify introduction for non-specialists
- [x] Add "physical intuition" paragraphs

---

## Priority Levels

### 🔴 CRITICAL (Must complete before submission)
1. ✅ Energy scale specification (Item A)
2. ✅ Equation numbering (Item G)
3. ✅ References & citations (Item H)
4. ✅ Code availability (Item I)
5. ✅ Honest statistical reporting (Item K)

### 🟡 IMPORTANT (Strongly recommended)
1. ✅ CKM limitations (Item B)
2. ✅ Figures & diagrams (Item F — partial)
3. ✅ Microscopic derivation statement (Item E)
4. ✅ Supplementary materials (Item J)
5. ✅ Clarity & Accessibility (Item L)

---

## Completion Tracking

### Overall Progress: ~25/35 items completed

**Last Updated:** 2026-02-17 (Final Integrity Sync)
**Next Review Date:** [Pre-Submission Final]
**Responsible:** Yui + Claude + Gemini Team

**File Location:** `v16.1/PUBLICATION_CHECKLIST.md`
**Version:** 1.2
**Status:** Ready for Preprint
