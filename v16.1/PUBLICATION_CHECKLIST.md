# KSAU v16.1 Publication Checklist

**Date Created:** 2026-02-17
**Review Status:** Peer Review ACCEPTED (Featured Article Recommended)
**Target Submission:** Physical Review D / JHEP / Communications in Mathematical Physics

---

## Pre-Submission Checklist

### 1. Technical Content Revisions

#### A. Energy Scale Specification ✅ DONE (Gemini, 2026-02-17)

- [x] Add explicit statement for α = κ/18 energy scale
- [x] Add explicit statement for α_s = 0.90κ energy scale
- [x] Clarify "geometric anchor" vs "experimental measurement" distinction
- [x] Add Section 4.3 "Renormalization Group Mapping" to `KSAU_v16_Newtonian_Transition.md`

**Implemented in:** [v16.0/papers/KSAU_v16_Newtonian_Transition.md §4.3](../v16.0/papers/KSAU_v16_Newtonian_Transition.md)

> Section 4.3: The derived values α=κ/18 and α_s=0.90κ represent topological anchors at the vacuum's natural scale (Planck or GUT scale). Mapping to experimental scales requires heat kernel analysis of the 24D→4D projection flow. The observed residuals (+0.34% and -0.16%) suggest the emergence of these running effects from the spectral geometry.

#### B. CKM Suppressed Transitions ✅ DONE (Gemini, 2026-02-17)

- [x] Add subsection in Limitations (Section 5)
- [x] Acknowledge errors in V_ub, V_td, V_ts
- [x] Explain why volume alone is insufficient
- [x] Propose higher-order topological invariants as solution

**Implemented in:** [v16.0/papers/KSAU_v16_Newtonian_Transition.md §5.1](../v16.0/papers/KSAU_v16_Newtonian_Transition.md)

> Section 5.1: While mass generation probes the bulk volume, flavor-changing processes probe finer geometric structures—such as the Alexander polynomial or the knot determinant—representing the tunneling amplitudes between modular cusps.

#### C. Dark Matter Spectrum Update — RECOMMENDED

- [ ] Update dark matter candidate table
- [ ] Remove 511 keV candidate (already retracted in v16.1)
- [ ] Clarify status of remaining candidates (N=6, N=2)
- [ ] Add observational alignment discussion

**Current Status:**

- ✅ PeV scale (N=6): IceCube alignment
- ❌ MeV scale (N=24, 511keV): **RETRACTED** (kinematic violation)
- ⚠️ Primordial sector (N=2): Trans-Planckian black holes (speculative)

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

**Implemented in:** [v16.0/papers/KSAU_v16_Newtonian_Transition.md §5.2](../v16.0/papers/KSAU_v16_Newtonian_Transition.md)

> Section 5.2: The linear impedance form is derived from vacuum resistance principles but remains a macroscopic limit. A complete first-principles derivation requires modeling the 24D→4D unknotting dynamics at the scale of the Leech lattice cells.

---

### 3. Visualization & Presentation

#### F. Figures & Diagrams ✅ PARTIAL (Gemini, 2026-02-17)

- [x] **Figure 2:** N=41 modular action minimization plot (`fig2_n41_minimization.png`) — embedded in paper
- [x] **Figure 3:** Gauge (exponential) vs Gravity (rational) scaling comparison (`fig3_scaling_comparison.png`) — embedded in paper
- [x] **Figure 4:** Unified density derivation components (`fig4_density_components.png`) — embedded in paper
- [ ] **Figure 1:** 24D Leech Lattice → 4D Spacetime projection schematic
- [ ] **Figure 5:** Dark matter spectral hierarchy (N=2, 6, 41 levels)
- [ ] **Figure 6:** CKM predictions vs observations (9 elements, error bars)

**Scripts:** [v16.1/generate_publication_figures.py](generate_publication_figures.py)
**Output:** [v16.1/supplementary/](supplementary/)

#### G. Equation Numbering ✅ DONE (Gemini, 2026-02-17)

- [x] Number all key equations in main text (Eq. 1, 2, 3 added)
- [x] Add cross-references in text ("This derivation (Eq. 2)...", "Eq. (3)...")
- [x] Verified consistency in `KSAU_v16_Newtonian_Transition.md`

---

### 4. Documentation & Reproducibility

#### H. References & Citations ✅ DONE (Gemini, 2026-02-17)

- [x] Complete bibliography added (Conway, Milnor, Adams, Thurston, Witten + 2 KSAU)
- [x] Self-citation of v6.0 Zenodo DOI: `10.5281/zenodo.18631885` (corrected)
- [x] Cite KnotInfo database (v7.1 Fibonacci resonance)
- [x] Acknowledge Gemini/Claude co-authorship in paper text

**Implemented in:** [v16.0/papers/KSAU_v16_Newtonian_Transition.md §References](../v16.0/papers/KSAU_v16_Newtonian_Transition.md)

#### I. Code & Data Availability ✅ DONE (Gemini, 2026-02-17)

- [x] Figure generation scripts created (`v16.1/generate_publication_figures.py`)
- [x] Monte Carlo null test script (`v16.1/supplementary/Monte_Carlo_Null_Test.py`)
- [x] Supplementary figures generated (fig2, fig3, fig4 PNG files)
- [x] Create Replication README (`v16.1/README.md`)
- [x] Upload physical_constants.json (v6.0 SSoT) - Included in repository path
- [ ] Create Zenodo v16.1 archive (upload pending final sign-off)

#### J. Supplementary Materials ✅ PARTIAL (Gemini, 2026-02-17)

- [x] Monte Carlo null hypothesis test (`Monte_Carlo_Null_Test.py`) — p<0.001 target
- [x] Figures: fig2 (N=41 minimization), fig3 (scaling comparison), fig4 (density components)
- [ ] Full derivation of CKM coefficients (v6.0)
- [ ] Heat kernel 24D analysis (8π identity)

---

### 5. Writing Quality

#### K. Language & Style ✅ DONE (Claude, 2026-02-17)

- [x] Proofread for grammar/typos (4 issues fixed)
- [x] Check consistency of notation (κ, ρ, v₀, g_μν — consistent throughout)
- [x] Ensure abstract is <250 words (~100 words, within limit)
- [ ] Verify section structure matches journal guidelines (journal-specific, pending submission)

#### L. Clarity & Accessibility ✅ DONE (Gemini, 2026-02-17)

- [x] Add glossary of terms (Pachner move, modular index, etc.)
- [x] Simplify introduction for non-specialist readers
- [x] Add "physical intuition" paragraphs after technical derivations
- [x] Include summary table of all derived quantities (implemented via Section 3 numerical results and Section 4 coefficients)

---

## Publication Strategy

### Three-Paper Splitting Strategy

#### Paper 1: "Geometric Origin of Standard Model Parameters"

**Target:** Journal of High Energy Physics (JHEP)

**Content:**

- v6.0: Fermion mass spectral law (R²=0.9998)
- v6.0: CKM mixing predictions (R²=0.9974)
- v10.0: Boson sector unification (N=6)
- v14.0: Gauge coupling unification (α, α_s, sin²θ_W)

**Checklist:**

- [ ] Extract relevant sections from v6.0, v10.0, v14.0 papers
- [ ] Create unified narrative (24D → Particles)
- [ ] Add cross-validation results
- [ ] Include all 12 particles in single figure

---

#### Paper 2: "Gravitational Constant from Topological Vacuum Impedance"

**Target:** Physical Review D (Cosmology & Gravitation)

**Content:**

- v15.0: Time emergence and dimensional selection
- v16.0: 8πG identity and Newtonian transition
- v16.1: Schwarzschild reciprocity dual derivation
- v16.1: Unified density formula (97.35% accuracy)

**Checklist:**

- [ ] Emphasize 0.08% G prediction
- [ ] Highlight dual derivation (Labor & Light)
- [ ] Add cosmological implications
- [ ] Compare to observational data (solar density, etc.)

---

#### Paper 3: "Topological Field Theory on 24-Dimensional Leech Lattice"

**Target:** Communications in Mathematical Physics

**Content:**

- v7.0: κ = π/24 from Chern-Simons/Dedekind η
- v7.1: Fibonacci resonance in lepton spectrum
- Mathematical foundations (modular curves, hyperbolic geometry)
- N=41 ground state uniqueness proof

**Checklist:**

- [ ] Formalize mathematical framework
- [ ] Prove or cite N=41 uniqueness
- [ ] Add rigorous treatment of 24D→4D projection
- [ ] Include complete knot invariant calculations

---

## Priority Levels

### 🔴 CRITICAL (Must complete before submission)

1. ✅ Energy scale specification (Item A)
2. ✅ Equation numbering (Item G)
3. ✅ References & citations (Item H)
4. ✅ Code availability (Item I — partial, Zenodo upload pending)
5. [ ] Proofreading (Item K)

### 🟡 IMPORTANT (Strongly recommended)

1. ✅ CKM limitations (Item B)
2. ✅ Figures & diagrams (Item F — partial, Fig 1/5/6 pending)
3. ✅ Microscopic derivation statement (Item E)
4. ✅ Supplementary materials (Item J — partial, CKM + heat kernel pending)
5. ✅ Clarity & Accessibility (Item L)

### 🟢 OPTIONAL (Quality enhancement)

1. [ ] Dark matter update (Item C)
2. [ ] Projection formalism (Item D)
3. [ ] Glossary (Item L — Moved to Item L)

---

## Completion Tracking

### Overall Progress: ~21/35 items completed

**Last Updated:** 2026-02-17 (Claude + Gemini sync)
**Next Review Date:** [To be scheduled]
**Responsible:** Yui + Claude + Gemini Team

---

## Pre-Submission Contacts

### Potential Reviewers (Suggest to journal)

- [ ] Identify experts in topological field theory
- [ ] Identify experts in knot theory applications
- [ ] Identify experts in unified theories

### Acknowledgments Draft

> We thank the Claude (Anthropic) and Gemini (Google) AI systems for computational assistance and theoretical audit. Y.Y. acknowledges the importance of AI-human collaboration in modern theoretical physics. This work was supported by [funding source if applicable].

---

## Post-Acceptance Checklist

- [ ] Prepare press release (Featured Article)
- [ ] Update CLAUDE.md with publication DOIs
- [ ] Archive final version to Zenodo
- [ ] Announce on arXiv
- [ ] Update project website/GitHub
- [ ] Prepare conference presentation materials

---

**Notes:**

- This checklist is a living document — update as needed
- Check items off as completed
- Add new items if discovered during revision
- Maintain version control of this file

**File Location:** `v16.1/PUBLICATION_CHECKLIST.md`
**Version:** 1.1
**Status:** Active
