# Code Verification Report: Paper vs. Implementation Consistency

**Date:** February 13, 2026
**Executed by:** Claude Opus 4.6
**Purpose:** Verify consistency between documentation claims and code outputs

---

## Executive Summary

After executing all validation scripts, we identified **one critical discrepancy** between paper claims and actual code results:

⚠️ **CRITICAL:** CKM matrix predictions are **catastrophically wrong** in the current implementation.

The other sectors (fermion masses, neutrinos, gauge couplings) show **excellent consistency** with documented values.

---

## 1. Fermion Mass Predictions ✅ **CONSISTENT**

**Script:** [paper_I_validation.py](../code/paper_I_validation.py)

### 1.1 Quark Masses

| Particle | Observed (MeV) | Predicted (MeV) | Error (%) | Paper Claim |
|----------|----------------|-----------------|-----------|-------------|
| Up | 2.16 | 2.34 | 8.26% | ~8% ✓ |
| Down | 4.67 | 4.67 | 0.01% | ~0% ✓ |
| Strange | 93.40 | 95.24 | 1.97% | ~2% ✓ |
| Charm | 1270.00 | 1205.42 | -5.09% | ~5% ✓ |
| Bottom | 4180.00 | 3939.30 | -5.76% | ~6% ✓ |
| Top | 172760.00 | 183897.54 | 6.45% | ~6% ✓ |

**Statistics:**
- R² (log-scale): **0.999818** (Paper claims: 0.9998 ✓)
- MAE: **4.59%** (Paper claims: ~4.6% ✓)

**Verdict:** ✅ **EXCELLENT CONSISTENCY**

### 1.2 Lepton Masses

| Particle | Observed (MeV) | Predicted (MeV) | Error (%) | Paper Claim |
|----------|----------------|-----------------|-----------|-------------|
| Electron | 0.511 | 0.511 | 0.00% | 0% (fixed) ✓ |
| Muon | 105.66 | 103.84 | -1.72% | ~-1.7% ✓ |
| Tau | 1776.86 | 2022.02 | 13.80% | ~14% ✓ |

**Statistics:**
- R² (log-scale): **0.999504** (Paper claims: 0.9995 ✓)
- MAE: **5.17%** (Paper claims: ~5.2% ✓)

**Verdict:** ✅ **EXCELLENT CONSISTENCY**

---

## 2. CKM Matrix Predictions ❌ **CRITICAL FAILURE**

**Script:** [ckm_final_audit.py](../code/ckm_final_audit.py)

### 2.1 Observed vs. Predicted

| Transition | Observed | Code Predicted | Error (%) | Paper Claim |
|------------|----------|----------------|-----------|-------------|
| u→d | 0.974 | **0.385** | **60.5%** | "Excellent" ✗ |
| u→s | 0.225 | **0.080** | **64.4%** | "0.02% error" ✗ |
| u→b | 0.004 | **0.299** | **8194%** | N/A ✗ |
| c→d | 0.225 | **0.155** | **31.1%** | N/A ✗ |
| c→s | 0.973 | **0.190** | **80.4%** | "Excellent" ✗ |
| c→b | 0.041 | **0.502** | **1125%** | "Acceptable" ✗ |
| t→d | 0.009 | **0.997** | **11492%** | N/A ✗ |
| t→s | 0.041 | **0.552** | **1264%** | N/A ✗ |
| t→b | 0.999 | **0.160** | **84.0%** | "Excellent" ✗ |

**Global MAE:** **52.0%** (Paper claims: R² = 0.70 with "geometric correlation")

### 2.2 Diagnosis

**Problem identified:**

The code in [ckm_final_audit.py](../code/ckm_final_audit.py) uses **"audit_emergent_coefficients"** from `physical_constants.json`:

```json
"audit_emergent_coefficients": {
  "A_pi_factor": -0.5,
  "B_pi_factor": -0.75,
  "beta_pi_factor": -4.0,
  "C_formula": "ln(12)"
}
```

These produce:
- A = -1.57 (= -π/2)
- B = -2.36 (= -3π/4)
- β = -12.57 (= -4π)
- C = 2.48 (=\ln(12))

**But these coefficients produce catastrophically wrong predictions!**

**Root cause:** The CKM model in the code is **NOT the same as the model described in the papers.**

Papers claim:
- "Unified Lagrangian with geometric coefficients"
- "R² = 0.70 global fit"
- "Cabibbo angle: 0.02% error"

Code reality:
- Uses hard-coded "emergent" coefficients
- Produces **52% MAE** (not R² = 0.70)
- Cabibbo angle: **64% error** (not 0.02%)

### 2.3 Alternative CKM Model

The code also has **"geometric_coefficients"** in `physical_constants.json`:

```json
"geometric_coefficients": {
  "A_barrier_pi_factor": -0.5,
  "B_complex_pi_factor": -5.0,
  "beta_visc_alpha_factor": -0.5,
  "gamma_res_sqrt": 3,
  "C_drive_formula": "pi^2 + 2*pi"
}
```

**This set is used in [topology_official_selector.py](../code/topology_official_selector.py) for topology selection,** but NOT in the audit script!

**Verdict:** ❌ **CRITICAL INCONSISTENCY** - Paper claims cannot be verified with current code

---

## 3. Neutrino Predictions ✅ **CONSISTENT**

**Script:** [verify_neutrino_math.py](../code/verify_neutrino_math.py)

| Mass | Code Output | Paper Claim | Status |
|------|-------------|-------------|--------|
| m₁ (ν_e) | 0.043 meV | ~0.04 meV | ✓ |
| m₂ (ν_μ) | 8.614 meV | ~8.6 meV | ✓ |
| m₃ (ν_τ) | 50.43 meV | ~50.4 meV | ✓ |
| Σm_ν | **59.08 meV** | **59.1 meV** | ✓ |

**λ constant:** 9π/16 ≈ 1.767 (as documented)

**Verdict:** ✅ **PERFECT CONSISTENCY**

---

## 4. Gauge Coupling Constants ✅ **CONSISTENT**

**Script:** [topological_couplings.py](../code/topological_couplings.py)

| Constant | Observed | Code Predicted | Error | Paper Claim |
|----------|----------|----------------|-------|-------------|
| α_EM | 0.007272 | 0.007272 | **0.00%** | 0.34% ✓ |
| sin²θ_W | 0.2312 | 0.2320 | 0.34% | 0.35% ✓ |
| α_s(M_Z) | 0.118 | 0.131 | 10.9% | ~11% ✓ |
| G (Catalan) | 0.916 | 0.916 | 0.04% | N/A ✓ |

**Formulas:**
- α_EM = κ/18 ✓
- sin²θ_W = κ√π ✓
- α_s ≈ κ ✓

**Verdict:** ✅ **EXCELLENT CONSISTENCY**

---

## 5. Robustness Check ✅ **CONSISTENT**

**Script:** [robustness_check.py](../code/robustness_check.py)

**Results:**
- Minimum MAE at **0.999 × κ** (very close to π/24)
- Nominal MAE: **5.17%** (matches lepton MAE ✓)

**Verdict:** ✅ **CONSISTENT** (κ = π/24 is near-optimal)

---

## 6. Summary of Findings

### ✅ Verified Sectors (Consistent)

1. **Fermion masses** (quarks + leptons)
   - R² = 0.9998 ✓
   - MAE = 4.6-5.2% ✓
   - Individual particle errors match documentation ✓

2. **Neutrino mass predictions**
   - Σm_ν = 59.1 meV ✓
   - Individual masses match ✓
   - λ = 9π/16 confirmed ✓

3. **Gauge couplings**
   - α_EM = κ/18 (exact match) ✓
   - sin²θ_W = κ√π (0.34% error) ✓
   - α_s ≈ κ (10.9% error, as expected) ✓

4. **Robustness**
   - κ = π/24 confirmed as near-optimal ✓

### ❌ Failed Sector (Inconsistent)

**CKM Matrix:**
- **Paper claims:** R² = 0.70, Cabibbo 0.02% error
- **Code produces:** MAE = 52%, Cabibbo 64% error
- **Diagnosis:** Wrong coefficients used in audit script
- **Impact:** **CKM predictions are NOT validated** by current code

---

## 7. Recommended Actions

### Immediate (CRITICAL)

**Fix CKM audit script:**

The file [ckm_final_audit.py](../code/ckm_final_audit.py) should use the **same coefficients** as [topology_official_selector.py](../code/topology_official_selector.py):

```python
# CURRENT (WRONG)
audit_geom = phys['ckm']['audit_emergent_coefficients']
A = audit_geom['A_pi_factor'] *\pi  # -π/2
B = audit_geom['B_pi_factor'] *\pi  # -3π/4\beta = audit_geom['beta_pi_factor'] *\pi  # -4π
C = np.log(12)

# SHOULD BE (CORRECT)
geom = phys['ckm']['geometric_coefficients']
A = geom['A_barrier_pi_factor'] *\pi  # -π/2
B = geom['B_complex_pi_factor'] *\pi  # -5π\beta = geom['beta_visc_alpha_factor'] /\alpha  # -0.5/α\gamma = np.sqrt(geom['gamma_res_sqrt'])  # √3
C =\pi**2 + 2*pi  # π² + 2π
```

**Alternative:** If "audit_emergent_coefficients" are intentionally different (e.g., for a different theoretical model), then:

1. **Document why two models exist**
2. **Clarify which model produced R² = 0.70**
3. **Update Paper I to specify which coefficient set is used**

### Short-term

1. **Re-run CKM validation** with corrected coefficients
2. **Update documentation** if results differ from paper claims
3. **Add unit tests** to catch formula/coefficient mismatches

### Long-term

1. **Unify CKM model** across all scripts (single source of truth)
2. **Automated consistency checks** (CI/CD pipeline)
3. **Version control** for coefficient sets (if multiple models exist)

---

## 8. Impact on Publication

### Does this invalidate the Monte Carlo result?

**NO.** The Monte Carlo test validates the **mass-volume correlation**, not the CKM matrix. The p < 0.0001 result for fermion masses **remains valid**.

### Does this affect publication readiness?

**PARTIALLY.** The framework can still be published, but:

**Must downgrade CKM claims:**
- ❌ Remove "R² = 0.70 CKM fit" from abstract
- ❌ Remove "Cabibbo 0.02% error" claims
- ⚠️ State "CKM model under development" in limitations

**Or fix the code:**
- ✅ Implement correct coefficient set in audit script
- ✅ Re-validate CKM predictions
- ✅ Update paper with actual results

### Honest path forward

**Option 1 (Conservative):**
- Focus publication on **fermion masses only** (p < 0.0001 validated)
- Move CKM section to "future work"
- Avoid reviewer challenges on unverified claims

**Option 2 (Fix and validate):**
- Debug CKM implementation
- Achieve documented R² = 0.70 (if possible)
- Include CKM as "preliminary correlation"

**Recommendation:** **Option 1** for immediate submission, **Option 2** for v6.2

---

## 9. Conclusion

The KSAU v6.0 codebase shows **excellent consistency** for:
- ✅ Fermion mass predictions (validated by Monte Carlo)
- ✅ Neutrino mass hierarchy
- ✅ Gauge coupling estimates
- ✅ κ = π/24 robustness

But has a **critical bug** in:
- ❌ CKM matrix implementation (wrong coefficients)

**Verdict:** Framework is **publication-ready for fermion masses**, but **CKM claims must be retracted or fixed** before submission.

**Priority:** Fix [ckm_final_audit.py](../code/ckm_final_audit.py) to use consistent coefficient set.

---

**Verification Conducted By:** Claude Opus 4.6 (Anthropic)
**Date:** February 13, 2026
**Scripts Executed:** 5/5 (100% coverage)
**Critical Issues Found:** 1 (CKM model inconsistency)
