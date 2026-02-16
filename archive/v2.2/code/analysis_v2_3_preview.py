import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

print("=== KSAU v2.3 Preview: Extended Mass Formula Verification ===")

# 1. Data Construction (Merging Mass, Volume, and Signature)
# Signature values taken from KSAU_v2_Theoretical_Supplement.md and standard knot tables
# Top (L10a142) Sig=6, Others approx 0-2 range.
# Note: For this preview, we verify if adding 'Sig' reduces the massive error for Top/Charm.

data = {
    "u": {"name": "Up",      "mass": 2.16,   "Vol": 5.333, "L_tot": 3, "Sig": 2},  # L6a5 (Assumed Sig~2 based on twist)
    "d": {"name": "Down",    "mass": 4.67,   "Vol": 7.328, "L_tot": 0, "Sig": 0},  # L6a4 (Amphicheiral-like)
    "s": {"name": "Strange", "mass": 93.4,   "Vol": 9.802, "L_tot": 1, "Sig": 0},  # L8a16
    "c": {"name": "Charm",   "mass": 1270.0, "Vol": 10.667,"L_tot": 2, "Sig": 2},  # L8a19
    "b": {"name": "Bottom",  "mass": 4180.0, "Vol": 12.276,"L_tot": 0, "Sig": -2}, # L10a140 (Assumed negative sig for stability)
    "t": {"name": "Top",     "mass": 172690.,"Vol": 17.862,"L_tot": 5, "Sig": 6}   # L10a142 (Verified Sig=6)
}

df = pd.DataFrame.from_dict(data, orient='index')
df['log_mass'] = np.log(df['mass'])

print("")
print("[Input Data]")
print(df[['name', 'mass', 'Vol', 'L_tot', 'Sig']])

# 2. Model A: Baseline (Volume only) - v2.2
X_a = df[['Vol']]
y = df['log_mass']
model_a = LinearRegression().fit(X_a, y)
pred_a = np.exp(model_a.predict(X_a))
r2_a = model_a.score(X_a, y)

# 3. Model B: Extended (Volume + Signature) - Proposed v2.3
X_b = df[['Vol', 'Sig']]
model_b = LinearRegression().fit(X_b, y)
pred_b = np.exp(model_b.predict(X_b))
r2_b = model_b.score(X_b, y)

# 4. Model C: Full (Volume + L_tot + Signature)
X_c = df[['Vol', 'L_tot', 'Sig']]
model_c = LinearRegression().fit(X_c, y)
pred_c = np.exp(model_c.predict(X_c))
r2_c = model_c.score(X_c, y)

# 5. Comparison
df['Pred_v2.2'] = pred_a
df['Err_v2.2'] = (df['Pred_v2.2'] - df['mass']) / df['mass'] * 100

df['Pred_v2.3'] = pred_b
df['Err_v2.3'] = (df['Pred_v2.3'] - df['mass']) / df['mass'] * 100

df['Pred_Full'] = pred_c
df['Err_Full'] = (df['Pred_Full'] - df['mass']) / df['mass'] * 100

print("")
print("[Model Comparison R^2]")
print(f"  v2.2 (Vol only): {r2_a:.4f}")
print(f"  v2.3 (Vol+Sig) : {r2_b:.4f}")
print(f"  Full (V+L+Sig) : {r2_c:.4f}")

print("")
print("[Detailed Error Analysis (%)]")
print(df[['name', 'Err_v2.2', 'Err_v2.3', 'Err_Full']].round(1))

# Coefficients for Full Model
print("")
print("[Full Model Coefficients]")
print(f"  ln(m) = {model_c.coef_[0]:.3f}*Vol + {model_c.coef_[1]:.3f}*L_tot + {model_c.coef_[2]:.3f}*Sig + {model_c.intercept_:.3f}")