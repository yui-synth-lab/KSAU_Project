import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import seaborn as sns
import os

print("=== KSAU v2.4 Prototype: Unified Lepton-Quark Analysis ===")

# 1. Unified Data Construction
# C2: Casimir factor (Lepton=0, Quark=4/3)
# Note: Using Writhe proxy and Linking number
data = [
    # Leptons (Data from v1.6 Paper A)
    {"name": "electron", "type": "lepton", "mass": 0.511,  "C": 3, "Sig": 2, "L": 0, "C2": 0.0},
    {"name": "muon",     "type": "lepton", "mass": 105.66, "C": 6, "Sig": 0, "L": 0, "C2": 0.0},
    {"name": "tau",      "type": "lepton", "mass": 1776.8, "C": 7, "Sig": 6, "L": 0, "C2": 0.0},
    
    # Quarks (Data from v2.3 Validation)
    {"name": "up",       "type": "quark",  "mass": 2.16,   "C": 6,  "Sig": 2,  "L": 3, "C2": 1.33},
    {"name": "down",     "type": "quark",  "mass": 4.67,   "C": 6,  "Sig": 0,  "L": 0, "C2": 1.33},
    {"name": "strange",  "type": "quark",  "mass": 93.4,   "C": 8,  "Sig": 1,  "L": 1, "C2": 1.33},
    {"name": "charm",    "type": "quark",  "mass": 1270.0, "C": 8,  "Sig": 3,  "L": 2, "C2": 1.33},
    {"name": "bottom",   "type": "quark",  "mass": 4180.0, "C": 10, "Sig": 0,  "L": 0, "C2": 1.33},
    {"name": "top",      "type": "quark",  "mass": 173000.,"C": 10, "Sig": 6,  "L": 5, "C2": 1.33}
]

df = pd.DataFrame(data)
df['log_mass'] = np.log(df['mass'])

# 2. Unified Regression
# Model: ln(m) = alpha*C + beta*Sig + gamma*L + delta*C2 + intercept
X = df[['C', 'Sig', 'L', 'C2']]
y = df['log_mass']

model = LinearRegression().fit(X, y)
df['pred_log_mass'] = model.predict(X)
df['pred_mass'] = np.exp(df['pred_log_mass'])
df['error_pct'] = (df['pred_mass'] - df['mass']) / df['mass'] * 100

r2 = model.score(X, y)

print("")
print(f"Unified Model R²: {r2:.4f}")
print(f"Coefficients:")
print(f"  Crossing (C): {model.coef_[0]:.3f}")
print(f"  Signature (Sig): {model.coef_[1]:.3f}")
print(f"  Linking (L): {model.coef_[2]:.3f}")
print(f"  ColorFactor (C2): {model.coef_[3]:.3f}")
print(f"  Intercept: {model.intercept_:.3f}")

print("")
print("Results Table:")
print(df[['name', 'mass', 'pred_mass', 'error_pct']].round(2))

# 3. Statistical Significance (P-value)
# With N=9, we expect p < 0.01
# Running simple permutation test
print("")
print("Running Permutation Test (N=9)...")
n_trials = 10000
random_r2 = []
for _ in range(n_trials):
    y_rand = np.random.permutation(y)
    random_r2.append(LinearRegression().fit(X, y_rand).score(X, y_rand))

p_value = np.mean(np.array(random_r2) >= r2)
print(f"Frequentist P-Value: {p_value:.6f}")

# 4. Save Artifacts
out_dir = "KSAU/publish/v2.3/figures/v2_4_preview"
os.makedirs(out_dir, exist_ok=True)

plt.figure(figsize=(10,6))
sns.scatterplot(data=df, x='log_mass', y='pred_log_mass', hue='type', s=200)
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--')
for i, txt in enumerate(df['name']):
    plt.annotate(txt, (df.log_mass[i], df.pred_log_mass[i]))
plt.title(f"Unified Fermion Mass Fit (N=9, R²={r2:.4f}, p={p_value:.4f})")
plt.savefig(f"{out_dir}/v2.4_unified_fit.png")

print("")
print(f"Preview figure saved to {out_dir}/v2.4_unified_fit.png")