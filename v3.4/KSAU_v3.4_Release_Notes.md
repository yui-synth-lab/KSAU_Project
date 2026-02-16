# KSAU v3.4 Release Notes: "The Occam Update"

**Date:** February 6, 2026
**Version:** 3.4
**Significance:** Statistical Robustness & Topological Refinement

## 1. Overview
KSAU v3.4 represents a critical maturation of the Knot-Structure-At-Universal theory. Following critical review of v3.3, we have refined the topological assignment for the Strange quark and conducted extensive statistical validation. The theory now stands on a foundation of $>5\sigma$ statistical significance with quantified confidence intervals.

## 2. Key Changes

### 2.1 Refined Strange Quark Assignment
We have corrected the Strange quark assignment from $L11n345$ (v3.3) to **$L10n95$**.
*   **Why:** Systematic search revealed $L10n95$ is the unique global minimum for the Strange mass slot within the 3-component link space.
*   **Result:**
    *   **Fit Quality:** MAE improved from 8.76% to **8.38%**.
    *   **Complexity:** Reduced crossing number from 11 to 10 (Occam's Razor).
    *   **Uniqueness:** Top-5 candidate analysis confirms $L10n95$ is statistically superior to alternative candidates.

### 2.2 Statistical Validation (The "Shield")
To address concerns of overfitting and selection bias, we introduce the **Statistical Shield Supplement** (`KSAU_v3.4_Statistical_Shield.md`), which includes:
*   **Bootstrap Analysis:** 10,000 iterations confirming parameter stability ($\gamma = 1.308 \pm 0.029$).
*   **Top-K Uniqueness:** Tables showing that for $u, d, s, c$, our assignments are the rank-1 unique solutions.
*   **LOO Cross-Validation:** Demonstrating the model's predictive power (Charm mass predicted to within 0.02%).

## 3. Revised Model Parameters
The fundamental scaling law $ln(m) = \gamma V + b'$ has been recalibrated:

*   **Slope ($\gamma$):** 1.3079 (was 1.302 in v3.3)
*   **Intercept ($b'$):** -7.9159 (was -7.89 in v3.3)
*   **$R^2$:** 0.9992

## 4. Known Issues & Future Directions (v4.0)
*   **Top/Bottom Tension:** While v3.4 maintains v3.3 assignments for stability, analysis suggests alternative candidates ($L10a146$ for Bottom, $L10a107$ for Top) could halve the global error. These are reserved for v4.0 pending theoretical justification.
*   **Theoretical Basis:** Deriving the linear\log-mass relation from first-principles TQFT remains the primary goal for v4.0.

## 5. Files Included

*   **`KSAU_v3.4_Unified_Paper.md`**: Full unified paper (authoritative version).
*   `KSAU_v3.4_Statistical_Shield.md`: Statistical supplement.
*   `KSAU_v3.4_Refined_Paper.md`: Earlier draft (superseded by Unified Paper).
*   `../v3.3/code/ksau_v3_4_robustness.py`: Validation script.
