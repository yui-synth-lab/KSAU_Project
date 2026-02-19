# Analysis of ξ LOO-CV Variance (v19.0 Handover)

**Status:** COMPLETED
**Date:** 2026-02-18
**Reference:** v20.0 Roadmap [HIGH-1]

## 1. Summary of Results
In the v19.0 phase, the structure growth clustering efficiency parameter $\xi$ was estimated using Leave-One-Out Cross-Validation (LOO-CV) across three major surveys. The resulting best-fit $\xi$ values showed significant variance:

| Excluded Survey | Best-fit $\xi$ | Predicted $\gamma$ | Target $S_8$ |
| --- | --- | --- | --- |
| DES Y3 (2021) | 0.7766 | 0.7636 | 0.759 |
| HSC Y3 (2023) | 0.6812 | 0.7373 | 0.776 |
| KiDS-Legacy (2025) | 0.4733 | 0.6802 | 0.815 |

- **Mean $\xi$:** 0.6437
- **Standard Deviation ($\sigma_\xi$):** 0.1265

## 2. Source of Variance: Systematic vs. Model Error

### 2.1 Systematic Error (Observational)
A portion of the variance is attributable to the inherent tensions between the surveys themselves. The $S_8$ values range from $0.759$ to $0.815$. 
- **DES vs. KiDS:** The $2\sigma$ tension in $S_8$ between DES and KiDS is a known cosmological puzzle, likely stemming from different shear-bias calibrations, photometric redshift distributions, and baryonic feedback modeling.
- **KSAU Sensitivity:** The KSAU model is highly sensitive to the $S_8$ input because $\xi$ is the sole parameter controlling the growth suppression in the static model.

### 2.2 Model Error (Theoretical)
The most significant finding is the **Scale-Dependent Failure**.
- **The Problem:** The v19.0 model treats $\xi$ as a global constant, effectively assuming that topological tension suppresses clustering equally at all scales $k$.
- **The Evidence:** Different surveys probe different effective scales ($k_{eff}$).
  - KiDS-Legacy probes relatively smaller scales compared to the core DES lensing bins.
  - The drop in $\xi$ (from 0.77 to 0.47) when moving towards the KiDS-dominated fit suggests that clustering suppression is **more efficient at smaller scales**.
- **The Verdict:** The static model error (neglect of scale dependence) dominates the variance. A single $\xi$ cannot simultaneously satisfy both the large-scale structure formation and small-scale lensing constraints.

## 3. Direction for v20.0
The high $\sigma_\xi$ (0.1265) provides the empirical justification for the transition to a **Scale-Dependent Phase Tension Model** ($\xi(k)$). The goal of v20.0 Section 1 is to replace the constant $\xi$ with a spectrum-based function derived from the 24-cell manifold's resonance hierarchy, thereby absorbing the variance into the model's geometric structure.

---
*KSAU Integrity Protocol - Scientific Writing Kernel*
