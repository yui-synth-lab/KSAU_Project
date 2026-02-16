
import numpy as np

# Physical Data
LEPTONS = {
    'e': {'mass': 0.511, 'N': 3},
    'mu': {'mass': 105.66, 'N': 6},
    'tau': {'mass': 1776.86, 'N': 7}
}

# Proposed Constants
G = 0.915965594
GAMMA_QUARK = (10/7) * G  # ~ 1.3085

print(f"Catalan Constant G = {G:.5f}")
print(f"Quark Slope (10/7 * G) = {GAMMA_QUARK:.5f}")

# Prepare Arrays
names = ['e', 'mu', 'tau']
masses = np.array([LEPTONS[q]['mass'] for q in names])
N = np.array([LEPTONS[q]['N'] for q in names])
N2 = N**2  # v3.3 Hypothesis: Lepton mass scales with N^2

ln_m = np.log(masses)

# 1. Linear Regression: ln(m) = slope * N^2 + intercept
A = np.vstack([N2, np.ones(len(N2))]).T
slope, intercept = np.linalg.lstsq(A, ln_m, rcond=None)[0]

print("\n--- Lepton Regression Results (N^2 Scaling) ---")
print(f"Slope (Fit): {slope:.5f}")
print(f"Intercept (Fit): {intercept:.5f}")

# 2. Comparison with Quark Slope
ratio = slope / GAMMA_QUARK
print(f"\nRatio (Lepton Slope / Quark Slope): {ratio:.5f}")
print(f"Is it 1/7? {1/7:.5f} (Diff: {abs(ratio - 1/7):.5f})")
print(f"Is it 1/10? {1/10:.5f} (Diff: {abs(ratio - 0.1):.5f})")
print(f"Is it G/10? {G/10:.5f}")

# 3. Check for Intercept Integer patterns
print(f"\nIntercept analysis: {intercept:.5f}")
print(f"Intercept + 7? {intercept + 7:.5f}")
print(f"Intercept / G? {intercept / G:.5f}")

# 4. Alternative Scaling? (Maybe N, not N^2?)
# Let's check linear N scaling briefly
A_n = np.vstack([N, np.ones(len(N))]).T
slope_n, intercept_n = np.linalg.lstsq(A_n, ln_m, rcond=None)[0]
print("\n--- Alternative: Linear N Scaling ---")
print(f"Slope (N): {slope_n:.5f}")
print(f"Intercept (N): {intercept_n:.5f}")
