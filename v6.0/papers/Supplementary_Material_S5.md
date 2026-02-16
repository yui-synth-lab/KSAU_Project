# Supplementary Material S5: Complete CKM Analysis

## Title: The Three-Factor Model and the Resolution of the Cabibbo Anomaly

This document provides the full data and statistical analysis for the CKM mixing model presented in Paper I, Section 4.3.

### S5.1 Dataset: All 9 CKM Transitions

| Transition | |V_ij| (Exp) | ΔV (Geometric) | Mean V̄ | Δgen |
|------------|--------------|----------------|---------|------|
| u → d      | 0.974        | 0.776          | 6.94    | 0    |
| u → s      | 0.225        | 2.980          | 8.04    | 1    |
| u → b      | 0.0036       | 3.737          | 12.02   | 2    |
| c → d      | 0.225        | 4.189          | 8.65    | 1    |
| c → s      | 0.973        | 0.433          | 9.75    | 0    |
| c → b      | 0.041        | 0.757          | 11.90   | 1    |
| t → d      | 0.008        | 6.421          | 11.95   | 2    |
| t → s      | 0.040        | 1.799          | 13.05   | 1    |
| t → b      | 0.999        | 1.042          | 15.20   | 0    |

### S5.2 Regression Analysis: R² Progression

1. **Model A (Volume Difference Only):**
   $$ \ln|V_{ij}| \propto -0.5 \Delta V $$
   R² = 0.44
   *Captures the general trend but fails for u→s vs c→b comparison.*

2. **Model B (Including Generation Penalty):**
   $$ \ln|V_{ij}| \propto -0.5 \Delta V - \alpha |\Delta \t\text{gen}| $$
   R² = 0.70
   *Explains generation suppression but leaves the Cabibbo Anomaly unresolved.*

3. **Model C (Three-Factor Model; fixed $A=-0.5$ on $\Delta V$):**
   $$ \ln|V_{ij}| \approx -0.5 \Delta V + \frac{\beta}{\bar{V}} - \gamma |\Delta \t\text{gen}|^2 $$
   R² = 0.68
   *In the current dataset, this constrained form does not improve over Model B; allowing the $\Delta V$ coefficient to float increases R² but changes its sign, indicating that the simple physical interpretation is not yet stable.*

### S5.3 Physical Constants

- $\beta$ and $\gamma$ are regression coefficients in the constrained Model C and should be treated as exploratory (they are sensitive to model constraints and sample size).

### S5.4 Reproduction Code

The following Python script reproduces the constrained regression for Model C (fixed $A=-0.5$ on $\Delta V$).

```python
import numpy as np
from sklearn.linear_model import LinearRegression

# Data
ln_V = np.log([0.974, 0.225, 0.0036, 0.225, 0.973, 0.041, 0.008, 0.040, 0.999])
DV = np.array([0.776, 2.980, 3.737, 4.189, 0.433, 0.757, 6.421, 1.799, 1.042])
MV = np.array([6.94, 8.04, 12.02, 8.65, 9.75, 11.90, 11.95, 13.05, 15.20])
DG = np.array([0, 1, 2, 1, 0, 1, 2, 1, 0])

# Constrained regression:\ln|V| + 0.5*DV =\beta*(1/MV) + g*(DG**2) + C
Y = ln_V + 0.5 * DV
X = np.stack([1/MV, DG**2], axis=1)
model = LinearRegression().fit(X, Y)

pred_lnV = -0.5 * DV + model.predict(X)
r2 = 1 - np.sum((ln_V - pred_lnV)**2) / np.sum((ln_V - np.mean(ln_V))**2)

print(f"R2 Score: {r2:.3f}")
print(f"beta, g: {model.coef_}")
print(f"C: {model.intercept_}")
```
