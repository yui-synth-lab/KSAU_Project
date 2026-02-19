# KSAU v24.0 Section 5 Report — Session 5

**Date:** 2026-02-18
**Session:** Session 5 (ng.md Session 4 REJECT Requirements)
**Status:** PARTIAL PROGRESS — R-1 ✓, R-6 ✓, R-4' △, R-3 ✗, R-2 ✗, R-5 ✗

---

## Overview

Session 5 addresses the REJECT requirements from `ng.md` (Session 4 verdict). The ng.md reviewer identified 6 fatal flaws and demanded corrections. This session executes the highest-priority items:

1. **R-4' (CRITICAL)**: Complete κ^n × α^m search with m extended to 20
2. **R-1**: ≥5 independent WL surveys (z<1) LOO-CV
3. **R-6**: Permutation test with ≥5 WL surveys

---

## R-4': Complete κ^n × α^m Search (ng.md Critical Requirement)

### What Session 4 Got Wrong

Session 4 searched n∈[1,100], m∈[0,**9**]. The reviewer found that m=12 (outside the search range) yields a superior candidate:

| Formula | log₁₀ | Error (dex) | Session 4 visible? |
|---------|--------|-------------|---------------------|
| **κ^36 × α^12** | **-51.96510** | **0.00847** | **NO (m=12 > 9)** |
| κ^55 × α^2 | -51.93086 | 0.02578 | YES ← false champion |
| κ^57 × α^1 | -52.01574 | 0.05910 | YES |
| κ^34 × α^13 | -51.88022 | 0.07641 | NO (m=13 > 9) |

**κ^36 × α^12 has 3× lower error than κ^55 × α^2.** Session 4's "best" was a false champion from artificial m truncation.

### Full Search Results (n∈[1,100], m∈[0,20])

- **Total candidates:** 2,100
- **Candidates within 0.01 dex:** 1
- **Candidates within 0.10 dex:** 5
- **Candidates within 1.00 dex:** 48

**48 candidates within 1 dex is NOT statistically significant** with 2 free integer parameters.

### Unit System Clarification (ng.md 欠陥 #3)

The target -51.957 is:
```
log₁₀(Λ_Planck2018_SI) = log₁₀(1.105 × 10⁻⁵² m⁻²) = -51.957
```

Key issue:
- κ = π/24 is **dimensionless**
- α = 1/48 is **dimensionless**
- κ^n × α^m is **dimensionless**
- Equating a dimensionless number to Λ (which has SI units of m⁻²) requires an unstated natural length scale

In Planck units: log₁₀(Λ_PL) ≈ -121.5 (completely different target). In cosmological units (h/Mpc)²: log₁₀(Λ_cosmo) ≈ -2.978. The match at -51.957 is unit-system dependent (raw SI).

### Honest Conclusion

- ✓ Full search completed (m extended to 20 per reviewer requirement)
- ✓ True best candidate identified: κ^36 × α^12 (error 0.008 dex)
- ✓ Session 4's T(10)=55 rationalization exposed as a posteriori
- ✓ Unit-system ambiguity documented
- ✗ No first-principles derivation exists (REMAINS OPEN)
- n=36=6² has no established physical motivation in the KSAU framework

**R-4' STATUS: △ PARTIALLY ADDRESSED** — honest analysis complete; first-principles derivation cannot be achieved by numerical search alone.

---

## R-1: 5 Independent WL Surveys LOO-CV

### Survey Dataset

| Survey | S8_obs | S8_err | k_eff | z_eff | Source |
|--------|--------|--------|-------|-------|--------|
| DES Y3 | 0.759 | 0.025 | 0.15 | 0.33 | Abbott et al. (2022) |
| CFHTLenS | 0.748 | 0.066 | 0.20 | 0.40 | Heymans et al. (2013) |
| DLS | 0.818 | 0.053 | 0.22 | 0.52 | Jee et al. (2016) |
| HSC Y3 | 0.776 | 0.033 | 0.35 | 0.60 | Dalal et al. (2023) |
| KiDS-Legacy | 0.815 | 0.021 | 0.70 | 0.26 | Asgari et al. (2021) |

Two new surveys added: CFHTLenS (independent CFHT/MegaCam footprint) and DLS (5 independent subfields, northern hemisphere).

### LOO-CV Results

| Survey | R₀_opt (Mpc/h) | S8_pred_z | S8_obs_z | Tension | Pass? |
|--------|----------------|-----------|----------|---------|-------|
| DES Y3 | 39.630 | 0.6877 | 0.6488 | +1.821σ | △ |
| CFHTLenS | 29.556 | 0.6542 | 0.6216 | +0.593σ | ✓ |
| DLS | 26.213 | 0.6128 | 0.6497 | -0.877σ | ✓ |
| HSC Y3 | 27.212 | 0.5921 | 0.5992 | -0.279σ | ✓ |
| KiDS-Legacy | 19.697 | 0.6885 | 0.7177 | -1.580σ | △ |

**LOO-CV MAE = 1.0302σ** (vs 1.356σ with 3 surveys in Session 4)

No boundary hits — v23.0 model valid for all 5 z<1 surveys.

**R-1 STATUS: ✓ ACHIEVED** — 5 independent WL surveys, LOO-CV successfully executed.

---

## R-3: k_eff × R₀ / (1+z)^β Invariant

| Survey | k_eff | R₀_loo | (1+z)^β | Invariant |
|--------|-------|--------|---------|-----------|
| DES Y3 | 0.15 | 39.630 | 1.8550 | 3.2045 |
| CFHTLenS | 0.20 | 29.556 | 2.0731 | 2.8515 |
| DLS | 0.22 | 26.213 | 2.4774 | 2.3278 |
| HSC Y3 | 0.35 | 27.212 | 2.7686 | 3.4400 |
| KiDS-Legacy | 0.70 | 19.697 | 1.6499 | 8.3566 |

**CV = 54.3%** (ng.md target: < 10%)

KiDS-Legacy is the critical outlier (invariant 8.36 vs mean 4.04 of others ≈ 2.8–3.4). The KiDS combination of high k_eff (0.70) and anomalously low z_eff (0.26) breaks the R₀ ∝ (1+z)^β / k_eff scaling. This is a fundamental model limitation requiring either:
1. A modified scaling relation for high-k_eff surveys
2. A different treatment of z_eff for KiDS (whose source redshift distribution peaks at z~0.5 despite z_eff=0.26)

**R-3 STATUS: ✗ FAIL** — CV = 54.3% >> 10%. KiDS systematic outlier. Model fix required.

---

## R-5: Tensions < 1σ

- 3/5 surveys achieve |tension| < 1σ (CFHTLenS, DLS, HSC Y3)
- 2/5 surveys have |tension| ≥ 1σ (DES Y3: +1.821σ, KiDS-Legacy: -1.580σ)
- All 5 within 2σ

MAE = 1.0302σ (improved from 1.356σ in Session 4 3-survey test)

**R-5 STATUS: ✗ FAIL** — not all surveys < 1σ.

---

## R-6: Permutation Test (5! = 120 permutations)

### Combinatorial Analysis
- C(8,5) = 56 ordered shell quintuples evaluated
- Winner quintuple: [8, 5, 4, 3, 2]
- Winner CV = 6.66%
- Combinatorial p-value: 1/56 = **0.0179 < 0.05** ✓

### Exact Permutation Test
- All 5! = 120 permutations of R₀ values evaluated
- Actual (physical) assignment CV = 6.6582% (rank 2 of 120)
- Permutations with CV ≤ actual: **2/120**
- **p-value = 0.0167 < 0.05** ✓

**R-6 STATUS: ✓ PASS** — p = 0.0167 < 0.05

### Caveats (to be noted in reviewer response)

1. **The physical assignment is rank 2** (not rank 1): one non-physical permutation achieves CV = 4.59% < 6.66% (physical). This means the physical k_eff ordering does NOT uniquely minimize CV; it is one of 2 nearly-equivalent solutions.

2. **R₀ ordering violation**: HSC Y3 R₀ (27.21) > DLS R₀ (26.21) despite HSC having larger k_eff (0.35 > 0.22). The anti-correlation prediction is violated between these two surveys.

3. **Bootstrap MC p = 0.7745**: With ±10% R₀ perturbations, 77.5% of random trials achieve CV ≤ actual. This suggests the CV threshold is not robust to measurement uncertainties.

The permutation test passes the stated criterion (p < 0.05), but caveats 1–3 indicate the result is fragile and may not survive a more rigorous test with additional surveys.

---

## Summary of Requirements

| Requirement | Session 5 Status | Detail |
|-------------|------------------|--------|
| R-1 (≥5 WL LOO-CV) | **✓ ACHIEVED** | 5 WL surveys, no boundary hits, MAE=1.03σ |
| R-2 (CMB z-growth model) | **✗ OPEN** | Not implemented |
| R-3 (k_eff invariant CV<10%) | **✗ FAIL** | CV=54.3% >> 10%, KiDS outlier |
| R-4' (complete search + honest) | **△ PARTIAL** | Best = κ^36×α^12; unit system issue; no first-principles |
| R-5 (<1σ all surveys) | **✗ FAIL** | 3/5 < 1σ, DES/KiDS at ±1.5-1.8σ |
| R-6 (perm test p<0.05) | **✓ PASS** | p=0.0167, but rank-2 caveat |

---

## Files Created/Modified

- `code/section_5_session5.py` — Session 5 Python script
- `data/wl5_survey_config.json` — 5-survey WL dataset (SSoT)
- `data/section_5_session5_results.json` — Numerical results
- `section_5_report.md` — This report

---

*KSAU v24.0 Session 5 Report — Simulation Kernel — 2026-02-18*
