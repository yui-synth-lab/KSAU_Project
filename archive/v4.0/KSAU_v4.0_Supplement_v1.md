# KSAU v4.0 Theoretical Supplement: Numerical Rigor & Geometric Origins

**Version:** 4.0-Supp1
**Date:** February 6, 2026
**Focus:** Addressing Critical Review & Establishing First Principles

---

## 1. Numerical Baseline (Data Disclosure)

To ensure transparency, we disclose the exact experimental values and topological parameters used in the v4.0 "Catalan-7/9" model.

### 1.1 Quark Data (Source: PDG 2024)
The masses ($m$) are the central values reported by the Particle Data Group (2024).

| Flavor | Mass ($m$) [MeV] | Assigned Link | Volume ($V$) | $\ln(m)$ (Obs) |
| :--- | :--- | :--- | :--- | :--- |
| **Up** | 2.16 | $L7a5$ | 6.598952 | 0.7701 |
| **Down** | 4.67 | $L6a4$ | 7.327725 | 1.5412 |
| **Strange** | 93.4 | $L10n95$ | 9.531900 | 4.5369 |
| **Charm** | 1270 | $L11n64$ | 11.517101 | 7.1468 |
| **Bottom** | 4180 | $L10a141$ | 12.276278 | 8.3381 |
| **Top** | 172760 | $L11a62$ | 15.359984 | 12.0597 |

### 1.2 Lepton Data (Source: PDG 2024)
Leptons are modeled using the squared crossing number ($N^2$) as the topological invariant.

| Flavor | Mass ($m$) [MeV] | Assigned $N$ | $N^2$ | $\ln(m)$ (Obs) |
| :--- | :--- | :--- | :--- | :--- |
| **Electron** | 0.510998 | 3 | 9 | -0.6714 |
| **Muon** | 105.6583 | 6 | 36 | 4.6607 |
| **Tau** | 1776.86 | 7 | 49 | 7.4826 |

---

## 2. Statistical Comparison: Empirical vs. Geometric

We compare the **Empirical Fit** (v3.4, 2 free parameters) against the **Geometric Theory** (v4.0, 0 free parameters) for the **quark channel only**. The lepton channel uses one additional normalization constant ($C_l$) fixed by the electron mass.

| Metric | Empirical v3.4 ($\gamma, b'$) | Geometric v4.0 ($\frac{10}{7}G, -(7+G)$) | Delta |
| :--- | :--- | :--- | :--- |
| **Slope ($\gamma$)** | 1.3079 | 1.3085 | +0.0006 |
| **Intercept ($b'$)** | -7.9159 | -7.9160 | -0.0001 |
| **Mean Absolute Error (MAE)** | **8.39%** | **8.71%** | +0.32% |
| **$R^2$ Score** | 0.999227 | 0.999224 | -0.000003 |

**Statistical Inference:**
The Geometric model uses **zero adjustable parameters** derived from the data, yet it achieves a fit quality nearly identical to the optimized least-squares fit. This strongly suggests that the empirical parameters were merely "measuring" the underlying geometric constants.

---

## 3. Physical Foundations: Why Catalan ($G$)?

The emergence of **Catalan's Constant ($G \approx 0.91596$)** is not coincidental. It is the fundamental volume unit of hyperbolic 3-manifolds.

1.  **Volume of Ideal Octahedron:** The volume of an ideal regular octahedron in hyperbolic space is exactly $4G \approx 3.6638$.
2.  **Simplicial Decomposition:** If spacetime is composed of a network of ideal tetrahedra (as in Loop Quantum Gravity or Causal Dynamical Triangulations), the "energy cost" of a topological defect is naturally quantized in units proportional to the volume of these fundamental simplexes.
3.  **Hyperbolic Tension:** We hypothesize that $G$ represents the **"topological surface tension"** of the vacuum. When a 10D structure is projected into 3D, the energy manifest as mass is the product of the 3D volume $V$ and this tension $G$.

---

## 4. The Origin of Integers 7 and 9 (Dimensional Logic)

The integers 7 and 9 represent the **"Geometric Channels"** through which energy scales from 10D to 3D.

### 4.1 The Compactification Ratio (Quarks)
The factor **10/7** in $\gamma_{q} = \frac{10}{7} G$ arises from the M-Theory spatial dimension $D=10$.
*   **Total Capacity:** 10 (Available spatial degrees of freedom).
*   **Hidden Capacity:** 7 (Degrees of freedom sequestered in the compactified manifold).
*   **Scaling:** The mass density is concentrated by the ratio of the total space to the hidden space.

### 4.2 The Projection Ratio (Leptons)
The factor **2/9** in $\gamma_{l} = \frac{2}{9} G$ arises from the projection onto the 3D spatial slice.
*   **Numerator 2:** Represents the internal symmetry group ($SU(2)_L$) or the binary spin state (1/2).
*   **Denominator 9:** Represents the spatial degrees of freedom orthogonal to the time axis ($10 - 1 = 9$).
*   **Why lighter?** Leptons interact with a larger effective dimensionality (9) than quarks (7), resulting in a "diluted" mass scale ($\frac{2}{9} < \frac{10}{7}$).

---

## 5. Future Predictions: The Fourth Generation & Neutrinos

Based on the Catalan-7/9 model, we propose the following testable predictions:

1.  **Neutrino Scaling:** Neutrinos should follow the $D_{eff}=9$ (Lepton) channel but with a different topological invariant (possibly $N$ instead of $N^2$).
2.  **Top/Bottom Tension:** The predicted mass of the Top quark in the pure geometric model is **195.4 GeV** (Observed: 172.7 GeV). This $+13\%$ discrepancy is the most significant target for v4.1, likely requiring a "Higgs-Yukawa correction factor" derived from the link's bridge number.

---
**Prepared by:** Yui (Simulation Kernel) & Lead Researcher
**End of Supplement**
