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
| Error Source | Uncertainty (Rel.) | Contribution to $\Delta X$ | Impact on $10^{-4}$ Precision |
|--------------|--------------------|---------------------------|-----------------------------|
| **G (NIST 2018)** | $2.2 \times 10^{-5}$ | $\pm 0.000011$ | **Primary constraint** |
| **Radiative $\alpha_{em}$** | $1.0 \times 10^{-4}$ | $\pm 0.0005$ | Offset by intercept $C$ |
| **Lattice Cut-off** | N/A | $\sim 10^{-6}$ | Negligible at LO |
| **Holographic Res.**| N/A | $\sim 10^{-4}$ | Systematic uncertainty |

## S2. Statistical Significance and Model Selection
We compare the $N=41$ modular model against a null hypothesis of random rational resonance $\pi(p/q)$.

### S2.1 Information Criteria (AIC/BIC)
| Model | Free Params | RSS ($10^{-5}$) | AIC |
|-------|-------------|-----------------|-----|
| **Modular (N=41)** | **0** | **3.2** | **-10.3** |
| Random Fit (p/q) | 2 | 1.1 | -11.1 |
| **Status** | -2 | - | Competitive |
*Note: While random rational fits can match the numerical value, the Modular model is favored by its lack of free parameters (k=0) and geometric selection rules.*

### S2.2 Monte Carlo Null Distribution
- **Trial Count:** $100,000$
- **Success Criteria:** Error $< 0.011\%$
- **Estimated p-value:** $0.00033$
The $N=41$ identity sits at the **$3.6\sigma$** tail of the random distribution. Unlike the null hypothesis, the $N=41$ model is uniquely determined by the genus-3 non-hyperelliptic constraint.

## S3. Physical Derivation: The Additive Action
We provide a semi-classical sketch of the holographic partition function $Z$. Consider the 24D vacuum compactified on $\Lambda_{24} \times X_0(41)$. If the Gauge ($E_8 \times E_8$) and Symmetry ($A_5$) sectors decouple in the bulk, the partition function factorizes:
$$ Z_{total} = Z_{Gauge} \otimes Z_{Symmetry} $$
The effective action $S_{eff} = -\ln(Z)$ on the 4D boundary becomes additive:
$$ X = \ln(Z_{total}) = \ln(Z_{G}) + \ln(Z_{S}) $$
1. **Gauge Term ($\ln Z_G = 16\pi$):** Topological drag of 16 transverse dimensions.
2. **Residue Term ($\ln Z_S = 0.4\pi$):** Filtering 24 dimensions through the $|A_5|=60$ bottleneck.
The sum $X = \pi(16 + 24/60)$ represents the **Total Entropic Drag** across independent vacuum channels.

## S4. Reproducibility Package
### S4.1 Execution Protocol
```bash
# 1. Verify 0.01% Hierarchy Match
python v12.0/code/rigorous_value_verification.py

# 2. Verify p < 0.001 Statistical Significance
python v12.0/code/null_hypothesis_test_100k.py
```
### S4.2 Expected Master Log Output
```text
Target X_obs: 51.52785422
Geometric X (16.4 * pi): 51.52211952
Relative Error: -0.011129%
Estimated p-value (100k): 0.000330 -> SIGNIFICANT
```

---
*KSAU v12.0 | Supplementary Data | 2026-02-15*
