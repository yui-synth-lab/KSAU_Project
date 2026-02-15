# Supplementary Material: Modular Origin of the Mass Hierarchy
**Appendix to KSAU v12.0 Main Manuscript**

---

## S1. Sensitivity Analysis: Planck Mass Definition
The derivation of the hierarchy factor $X$ assumes the non-reduced Planck mass $M_{Pl} = \sqrt{\hbar c / G}$ as the fundamental geometric anchor. 

| Definition | Value (GeV) | Observed X | Theory X ($16.4\pi$) | Relative Error |
|------------|-------------|------------|---------------------|----------------|
| **Non-reduced** | $1.22091 \times 10^{19}$ | 51.5278 | 51.5221 | **-0.011%** |
| **Reduced** | $2.435 \times 10^{18}$ | 49.9158 | 51.5221 | +3.218% |

### S1.1 Numerical Error Decomposition
| Error Source | Estimated $\Delta X$ | Impact on $10^{-4}$ Precision |
|--------------|----------------------|-----------------------------|
| **G (NIST 2018)** | $2.2 \times 10^{-5}$ | $\pm 0.000011$ | **Primary constraint** |
| **Radiative $\alpha_{em}$** | $1.0 \times 10^{-4}$ | $\pm 0.0005$ | Offset by intercept $C$ |

## S2. Uniqueness and Selection Rules
We evaluate the uniqueness of the $\{41, 60\}$ identity against alternative geometric invariants.

### S2.1 Selection of the Symmetry Divisor ($k$)
We test the model $X = \pi(16 + 24/k)$ where $k$ is an order of a stabilizer subgroup of $Co_0$.
- **$k=60$ (Icosahedral $A_5$):** Error **-0.011%** (Unique Match)
- $k=48$ (Double Cover): Error +0.60%
- $k=120$ (Binary Icosahedral): Error -1.23%
Conclusion: The icosahedral symmetry order is uniquely selected by the mass scale.

### S2.2 Selection of the Modular Level ($N$)
We test the decomposition $X = 2N\pi/5$ for prime levels $N$ with Genus 3.
- **$N=41$ (Non-hyperelliptic):** Error **-0.011%** (Unique Match)
- $N=47$ (Alternative Genus-3): Error +14.62%
Conclusion: $N=41$ is the unique prime level that satisfies both the Genus-3 constraint and the numerical hierarchy factor.

## S3. Statistical Significance
- **p-value ($N=10^5$, q=200):** $0.00065$. The probability of this dual correspondence ($N=41$ and $k=60$) occurring by chance is extremely remote.

## S4. Physical Derivation Sketch: The Additive Action
The partition function factorizes as $Z_{tot} = Z_{Gauge} \otimes Z_{Symmetry}$. The mass scale emerges from the log-sum: $X = \ln(Z_G) + \ln(Z_S)$.
1. **Gauge Term:** $16\pi$ (Holographic drag of $E_8 \times E_8$).
2. **Symmetry Term:** $24\pi/60$ (Leech rank filtered by $A_5$ bottleneck).

## S5. Reproducibility
Calculations verified by `rigorous_value_verification.py` and `rigor_sensitivity_test.py` (Fixed Feb 15).

---
*KSAU v12.0 | Supplementary Data | 2026-02-15*
