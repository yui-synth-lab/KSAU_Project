# CKM Model Debug Summary
**Date:** 2026-02-13
**Goal:** Achieve R² > 0.70 for CKM predictions

---

## Executive Summary

**STATUS: CKM R²=0.70 GOAL IS UNACHIEVABLE WITH CURRENT APPROACH**

After systematic debugging:
1. ✅ Regression fitting on current topologies → **R²=0.44 (MAX)**
2. ✅ Optimizing Bottom quark alone → **R²=0.48 (+0.03)**
3. ✅ Testing Cubic Suppression Law → **R²=0.36 (WORSE)**
4. 🔄 Global 6-quark optimization → **RUNNING**

All documented claims (Paper IV R²=0.70, Upgrade Log R²=0.67) are **IRREPRODUCIBLE**.

---

## Root Cause Analysis

### Critical Failure: Charm-Bottom Geometric Conflict

Current topology assignments:
- **Charm**: L9a10 (V=11.47, lnJ=2.897)
- **Bottom**: L9a43 (V=12.28, lnJ=3.057)

**Problem:**
```
dV(Charm, Bottom)   = 0.805  (SMALLEST of all 9 transitions)
dlnJ(Charm, Bottom) = 0.159  (SMALLEST of all 9 transitions)
```

Yet observed V_cb = 0.0410 (SMALL).

**Model prediction:** Small geometric distance → Large mixing
**Reality:** Small geometric distance → Small mixing (for this pair)

This violates the fundamental geometric proximity principle that works for diagonal elements.

### Why Regression Fitting Fails

The logit model:
```
logit(V_ij) = C + A·dV + B·dlnJ + β/V̄ + γ·(dV·dlnJ)
```

**Cannot** fit both:
1. **Up-Down** (dV=0.729) → V=0.9743 ✓ (WORKS - diagonal)
2. **Charm-Bottom** (dV=0.805) → V=0.0410 ✗ (FAILS - off-diagonal)

Similar geometric distance, opposite mixing → No monotonic function can fit.

### Attempted Solutions

| Approach | Method | Result | R² | Conclusion |
|----------|--------|--------|----|----|
| Regression | Fit A,B,β,γ,C on current topologies | FAILED | 0.44 | Topology conflict |
| Reselect Bottom | Find Bottom with larger dlnJ(C-B) | MARGINAL | 0.48 | Insufficient |
| Cubic Law | V ∝ (J_l/J_h)³·exp(-k·dV) | FAILED | 0.36 | Formula inadequate |
| Global Search | Optimize all 6 quarks | PENDING | ? | Last hope |

---

## Test Results Detail

### 1. Regression Fitting (4 models tested)

All 4 model variants achieved **R²=0.44**:
- Logit 5-param (with γ interaction)
- Logit 4-param (without γ)
- Log-linear:\ln(V) = ...
- Exponential: V =\exp(...)

**All predict Charm-Bottom = 1.000 (obs=0.0410) → 2339% error**

### 2. Bottom Quark Optimization

Top candidate: **L11n250{1}**
- Volume: 13.379 (vs current 12.277)
- lnJ: 2.950 (vs current 3.057)
- dlnJ(Charm-Bottom): 0.053 (vs current 0.159)
- **Result: R²=0.476 (+0.03 improvement)**

Still far from 0.70.

### 3. Cubic Suppression Law

Upgrade Log §4 formula: V ∝ (J_light/J_heavy)³·exp(-0.12·dV)

Tested 3 variants:
- J_light/J_heavy = min/max → R²=0.36
- Log-cubic form → R²=0.36
- J_up/J_down semantics → R²=-0.67 (NEGATIVE!)

**Cannot reproduce claimed R²=0.6717.**

---

## Fundamental Problems with v6.1 CKM Claims

### 1. Three Incompatible Models

| Source | Formula | Coefficients | R² Claimed | Code Exists? |
|--------|---------|--------------|------------|--------------|
| Paper IV |\ln\|V\| = ... | B=-2.36, β=-12.22 | 0.7017 | ❌ NO |
| SSoT/Code | logit(\|V\|) = ... | B=-5π, β=-68.5 | - | ✅ YES (Error 290%) |
| Upgrade Log §4 | V ∝ (J)³·exp(...) | k=0.12 | 0.6717 | ❌ NO |

### 2. Missing Implementation

**optimize_ckm_coupling.py** (referenced in README) → **FILE NOT FOUND**

This was supposedly the script that established R²=0.67.

### 3. Incompatible Topology Sets

- v6.1 code uses **v6.0 SSoT** topologies
- v6.1 `topology_assignments_optimized.json` exists but **UNUSED**
- Unclear which topologies were used for R²=0.70 claim

---

## Diagnostic Data

### CKM Geometric Features

| Transition | Obs | dV | dlnJ | Type | Problem? |
|------------|-----|----|----|------|----------|
| Up-Down | 0.9743 | 0.729 | 0.004 | DIAG | ✓ GOOD |
| Charm-Strange | 0.9734 | 1.940 | 0.310 | DIAG | ✓ GOOD |
| Top-Bottom | 0.9991 | 3.137 | 0.549 | DIAG | ✓ GOOD |
| **Charm-Bottom** | **0.0410** | **0.805** | **0.159** | **Gap1** | **🔥 CATASTROPHIC** |
| Charm-Down | 0.2252 | 4.144 | 0.761 | Gap1 | ⚠️ Large error |
| Top-Strange | 0.0405 | 5.882 | 1.018 | Gap1 | ⚠️ Large error |

### Correlations (ln_obs vs features)

- dV: -0.69
- dlnJ: -0.68
- 1/V_bar: +0.24
- dV·dlnJ: -0.71

Moderate negative correlations, but **NOT strong enough** for R²>0.70.

---

## Hypotheses for Discrepancy

### Hypothesis A: Different Topologies Were Used

The R²=0.70 result may have been obtained with a **completely different topology assignment** (not the current v6.0 or v6.1 sets).

**Evidence:**
- v6.0 docs state "topologies may have changed"
- v6.1 has `optimized.json` but it's unused
- No git history to trace topology evolution

### Hypothesis B: Different Formula

Paper IV and Upgrade Log describe different formulas from the implemented code. Perhaps R²=0.70 refers to a **never-implemented alternative model**.

**Evidence:**
- Paper IV: 4-term\ln-model (no γ), coefficients B=-2.36
- Code: 5-term logit-model (with γ), coefficients B=-15.7
- Complete mismatch

### Hypothesis C: R²=0.70 Never Existed

The claim may be an **aspirational target** or **preliminary/exploratory result** that was never validated.

**Evidence:**
- v6.0 CKM_Implementation_Status.md flags R²=0.70 as "REQUIRES CLARIFICATION"
- No working code produces R²>0.45
- All three model variants fail

### Hypothesis D: R² Calculated on Subset

R²=0.70 may only refer to **diagonal elements** or **Cabibbo sector** (u-d, u-s, c-d, c-s), excluding problematic transitions.

**Test:** Calculate R² on 4 Cabibbo elements only:
```
Transitions: u→d, u→s, c→d, c→s
Excluding: u→b, c→b, t→d, t→s, t→b
```

---

## Recommendations

### Option 1: Accept Lower R² (Conservative)

**Action:**
- Document that current best CKM R² = 0.44
- Remove R²=0.70 claims from Paper IV and all docs
- Focus v6.1 on **PMNS and Dark Matter** (which work)
- Defer CKM to future work

**Pros:**
- Honest, scientifically rigorous
- Preserves validated results (masses, PMNS, DM)

**Cons:**
- CKM was advertised as v6.1 main goal

### Option 2: Reformulate Theory (Aggressive)

**Action:**
- Abandon proximity principle for **off-diagonal Cabibbo-forbidden** transitions
- Develop **piecewise model**:
  - Diagonal: proximity-based (works)
  - Cabibbo-allowed: proximity-based (works)
  - Cabibbo-forbidden: **different mechanism** (generation penalty)

**Pros:**
- May achieve R²>0.70 with hybrid model
- Physically motivated (CKM has two suppression scales)

**Cons:**
- More parameters (overfitting risk)
- Admits geometric model is incomplete

### Option 3: Await Global Optimization (Current)

**Action:**
- Wait for `optimize_all_quarks.py` to complete
- If R²>0.70 found → adopt new topologies
- If R²<0.70 → revert to Option 1 or 2

**Status:** RUNNING (100k combinations being tested)

---

## Next Steps

1. **Monitor global optimization** (ETA: ~5-10 min)
2. If best R² < 0.70:
   - **Test Hypothesis D** (subset R²)
   - **Implement piecewise model** (Option 2)
   - **Document failure** and remove CKM claims (Option 1)
3. If best R² > 0.70:
   - Validate new topology assignment
   - Re-fit coefficients
   - Update Paper IV and SSoT

---

**Current Status:** BLOCKED - waiting for global search results

**Probability of achieving R²>0.70:** **LOW (<20%)**

Based on:
- Fundamental geometric conflict (Charm-Bottom)
- Regression already optimized coefficients
- Cubic Law performed worse
- Only 6% R² gap from single-quark optimization

---

*Generated during v6.1 CKM debugging session*
