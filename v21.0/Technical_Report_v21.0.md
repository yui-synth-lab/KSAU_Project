# KSAU v21.0 Technical Report: Filament Branching & Growth Evolution

**Date:** 2026-02-18
**Author:** Gemini (KSAU Simulation Kernel)
**Status:** REJECTED (gamma threshold 0.70 not met)

## 1. Executive Summary

v21.0 has investigated the topological origin of the cosmic web's filament branching and its impact on the $\sigma_8$ tension. 
We have successfully derived a model for the branching number $B_{ksau} = 3.9375$ from the 24-cell's symmetry corrected by the fractal deviation $\alpha = 1/48$.
However, the statistical validation remains below the project's strict success criteria. Both the static filament model (Section 1) and the unified dynamic model (Section 2) have been rejected based on LOO-CV growth index $\gamma > 0.70$.

## 2. Audit Findings & Corrective Actions

In response to the Auditor's report (2026-02-18), the following corrections have been applied:

### 2.1 Unified Model Status (CRITICAL-1)
The unified model in `unified_model_results.json` has been updated with dynamic growth factor integration (redshift evolution) as requested. While this provides more physical consistency, the resulting $\chi^2$ remains high, particularly due to the KiDS-Legacy dataset. The status is confirmed as **REJECTED**.

### 2.2 Branching Number Clarification (CRITICAL-2)
The value $B_{predicted} = 3.9375$ is a theoretical prediction derived from the tripartite decomposition of the 24-cell. It is compared against the observational benchmark $B \approx 3.94$ (Colberg 2007). The SSoT has been updated to distinguish between these values.

### 2.3 Growth Index $\gamma_{app}$ and S8 Tension (CRITICAL-3)
The derivation of $\gamma_{app} \approx 0.62$ explains the trend towards higher growth indices in LSS data. However, the current model's absolute $S_8$ predictions do not fully resolve the tension across all surveys (residuals of $3.3\sigma$ for KiDS-Legacy persist).


## 3. Section 1: Filament Branching Model (LOO-CV)

- **Theory**: Growth suppression factor $F_{branching} = B_{predicted} / B_{eff} \approx 0.984$.
- **Result**: $\gamma_{avg} = 0.822 \pm 0.144$.
- **Verdict**: **REJECTED** ($\gamma > 0.70$).
- **Analysis**: The static filament branching factor is insufficient to bring the growth index down to the $\Lambda$CDM-like threshold.

## 4. Section 2: Dynamic Coherence Length $R_{cell}(z)$

- **Theory**: Redshift-dependent resolution $R_{cell}(z) = R_0 (1+z)^{-\beta}$ with $\beta = D \approx 1.98$.
- **Status**: Single-point prediction successful, but requires full LOO-CV to claim "Validated" status.

## 5. Limitations

- **Double-Strand Assumption**: The hypothesis that the 8 incident edges split into two independent 4-strand groups (double-strand) still requires further geometric derivation to move from "Geometrically Motivated" to "Fully Derived".
- **LSS Comparison**: The benchmark value $B = 3.94$ represents a mean value in complex simulations; the exact integer-edge nature of the 24-cell projection requires more rigorous mapping to the "skeleton" of the cosmic web.

---
*KSAU Simulation Kernel (Gemini)*
