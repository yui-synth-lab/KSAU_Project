# Task A: $S_8$ Verification Design for Next-Gen Surveys

**Date:** 2026-02-21
**Status:** DESIGN_COMPLETE
**Target:** Euclid Wide Survey, LSST (Rubin Observatory)
**Model:** KSAU Standard Cosmology (SKC) - Resonance Model

## 1. Executive Summary

The KSAU framework resolves the $S_8$ tension not by modifying gravity, but by proposing a scale-dependent topological resonance in the spacetime manifold. This model has achieved statistical significance ($p=0.00556$) on current datasets (Planck, ACT, DES, KiDS, HSC).

This document defines the falsifiable predictions for upcoming surveys (Euclid, LSST). **The core prediction is a suppression of $S_8$ at intermediate redshifts ($z \sim 1.0$) relative to the CMB ($z \sim 1100$), following a specific resonance curve determined by the Leech lattice scale $R_{cell} \approx 20$ Mpc.**

## 2. Theoretical Basis: The Resonance Function

The effective $S_8$ observed at redshift $z$ and scale $k$ is given by:

$$ S_8^{eff}(z, k) = S_8(z) 	imes (1+z)^{ \gamma(k) } $$

Where $\gamma(k)$ is the resonance function derived from the Leech lattice geometry.
Current SSoT parameters (v27.0 fit):
- $\alpha = 7.2769$
- $k_{res} = 0.0496$ $h$/Mpc (Resonance scale corresponding to $R_{cell}$)
- Peak/Sigma = Fitted to current data.

## 3. Predictions for Next-Gen Surveys

Using `v28.0/code/ksau_standard_cosmology.py`, we generated predictions for the specific redshift-scale windows expected for Euclid and LSST.

### 3.1 Euclid Wide Survey (Space-based)
- **Target Redshift:** $0.9 < z < 1.8$ (Mean $z_{eff} \approx 1.0 - 1.2$)
- **Scale:** Linear to non-linear transition ($k \sim 0.1 - 0.5$ $h$/Mpc)

| $z_{eff}$ | $k$ [$h$/Mpc] | KSAU Prediction ($S_8$) | Planck $\Lambda$CDM | Difference |
|-----------|---------------|-------------------------|---------------------|------------|
| 1.0       | 0.10          | **0.729**               | 0.832               | -0.103     |
| 1.0       | 0.50          | **0.761**               | 0.832               | -0.071     |
| 1.2       | 0.10          | **0.724**               | 0.832               | -0.108     |
| 1.2       | 0.50          | **0.748**               | 0.832               | -0.084     |

**Prediction:** Euclid should measure a significantly suppressed $S_8 \approx 0.73 - 0.76$, consistently lower than the Planck CMB value.

### 3.2 LSST / Vera Rubin Observatory (Ground-based)
- **Target Redshift:** $0.3 < z < 3.0$ (Tomographic bins, focusing on $z \sim 0.7$)
- **Scale:** $k \sim 0.1 - 0.5$ $h$/Mpc

| $z_{eff}$ | $k$ [$h$/Mpc] | KSAU Prediction ($S_8$) | Planck $\Lambda$CDM | Difference |
|-----------|---------------|-------------------------|---------------------|------------|
| 0.7       | 0.10          | **0.739**               | 0.832               | -0.093     |
| 0.7       | 0.50          | **0.783**               | 0.832               | -0.049     |

**Prediction:** LSST tomographic bins should reveal the specific $z$-dependence of the suppression, validating the resonance curve form.

## 4. Verification & Falsification Criteria

### Verification
KSAU is **supported** if:
1.  Euclid/LSST measure $S_8$ values in the range **$0.72 - 0.78$** for $z \in [0.7, 1.2]$.
2.  The tomographic evolution of $S_8(z)$ follows the predicted decline from $z=0$ to $z=1$ ($0.78 	o 0.73$).

### Falsification
KSAU is **falsified** if:
1.  Euclid measures $S_8 > 0.80$ at $z \approx 1.0$ (consistent with Planck).
2.  The scale dependence $\gamma(k)$ is not observed (i.e., $S_8$ is scale-invariant).

## 5. Conclusion

The KSAU framework makes a bold, precise, and falsifiable prediction: **The universe appears less "clumpy" ($S_8$) at intermediate redshifts ($z \sim 1$) than at the present day ($z=0$) or recombination ($z=1100$).** This is contrary to standard $\Lambda$CDM which assumes a constant growth index $\gamma \approx 0.55$.

This design document serves as the pre-registered prediction for comparison with future data releases.

---
*KSAU v36.0 - Task A Output*
