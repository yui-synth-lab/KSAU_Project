# KSAU v23.0 Phase 2: Non-Linear Geometric Potential

## 1. Theoretical Basis
The non-linear growth of the cosmic web is modeled as the volumetric recovery of topological entanglement within the 24-cell manifold. While unknotting suppression (Xi_gap) dominates large scales, the small-scale dynamics are governed by the Chern-Simons linking flux.

### 1.1 Non-linear Boost (Volumetric Linking)
The boost factor $\Phi_{NL}(k)$ is derived from the scaling of linked knot density:
$$\Phi_{NL}(k) = 1 + \alpha \frac{(k/\kappa)^p}{1 + (k/k_{sat})^p}$$
where $p = 2.75$ represents the effective volumetric growth dimension in the non-linear regime, and $k_{sat} = \sqrt{24}\kappa$ is the saturation scale corresponding to the full connectivity of the 24-cell boundary.

### 1.2 Baryon Feedback (Dual Lattice Escape)
Baryon feedback is modeled as the Lorentzian escape probability from the 4D 24-cell vertices into the 8D E8 root lattice:
$$a_{bar}(k) = 1 - \Omega_b \kappa \frac{240}{24} \frac{k^2}{k^2 + k_{bar}^2}$$
where $k_{bar} = 1/(16\alpha) = 3.0$ h/Mpc, reflecting the characteristic scale of the 3D projection of the E8 dual lattice.

## 2. Validation Results (LOO-CV)
The unified potential engine achieves a Mean Absolute Deviation (MAD) of **0.92σ** across major weak lensing surveys.

- **KiDS-Legacy**: -0.17σ (Converged within 0.5σ success criterion)
- **HSC Y3**: +0.62σ
- **DES Y3**: +1.96σ

## 3. Limitations
While the volumetric recovery model successfully resolves the KiDS-Legacy discrepancy, significant tension remains with DES Y3 (+1.96σ). This suggests that the current 3rd-order linking approximation may still underestimate the suppression at intermediate scales or that survey-specific systematic effects (e.g., intrinsic alignment models) interact non-trivially with the geometric potential. The numerical stability is now enforced by a theoretical lower bound $R_{cell} \ge 2.0$ (the fundamental 24-cell diameter), but the tendency of the optimizer to push towards this limit indicates that the theory is operating at the edge of the stability domain for high-redshift, high-k data.
