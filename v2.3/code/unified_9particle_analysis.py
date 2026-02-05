import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ============================================================================
# STEP 1: FINAL VERIFIED DATA INPUT (v2.4)
# ============================================================================

print("="*70)
print("KSAU v2.4: 9-PARTICLE UNIFIED ANALYSIS (FINAL DATA)")
print("="*70)

# Experimental masses (PDG 2024) in MeV
MASSES = {
    'e': 0.511, 'mu': 105.66, 'tau': 1776.86,
    'u': 2.16, 'd': 4.67, 's': 93.4, 'c': 1270.0, 'b': 4180.0, 't': 173000.0
}

# Lepton Data (v1.6.1 Paper A + Pseudo-Volume Calculation)
LEPTON_DATA = {
    'e':   {'Vol': 0.739, 'Sig': 0, 'L': 0, 'C2': 0.0},
    'mu':  {'Vol': 5.693, 'Sig': 0, 'L': 0, 'C2': 0.0},
    'tau': {'Vol': 6.645, 'Sig': 0, 'L': 0, 'C2': 0.0}
}

# Quark Data (v2.3 Final Validation assignments)
QUARK_DATA = {
    'u': {'Vol': 5.333,  'Sig': 2,  'L': 3, 'C2': 1.333}, # L6a5
    'd': {'Vol': 7.328,  'Sig': 0,  'L': 0, 'C2': 1.333}, # L6a4
    's': {'Vol': 9.802,  'Sig': 0,  'L': 1, 'C2': 1.333}, # L8a16
    'c': {'Vol': 8.793,  'Sig': 4,  'L': 4, 'C2': 1.333}, # L8a17
    'b': {'Vol': 12.276, 'Sig': -2, 'L': 0, 'C2': 1.333}, # L10a141
    't': {'Vol': 11.867, 'Sig': 6,  'L': 5, 'C2': 1.333}  # L10a153
}

def build_dataset():
    data = []
    for p, m in MASSES.items():
        row = {'particle': p, 'mass': m, 'ln_m': np.log(m)}
        if p in LEPTON_DATA:
            row.update(LEPTON_DATA[p])
            row['type'] = 'lepton'
        else:
            row.update(QUARK_DATA[p])
            row['type'] = 'quark'
        data.append(row)
    return pd.DataFrame(data)

# ============================================================================
# STEP 2: REGRESSION & STATISTICAL SIGNIFICANCE
# ============================================================================

df = build_dataset()

# Model: ln(m) = alpha*Vol + beta*Sig + gamma*L + delta*C2 + intercept
X = df[['Vol', 'Sig', 'L', 'C2']]
y = df['ln_m']

model = LinearRegression().fit(X, y)
df['pred_ln_m'] = model.predict(X)
df['pred_m'] = np.exp(df['pred_ln_m'])
df['error_pct'] = (df['pred_m'] - df['mass']) / df['mass'] * 100

r2 = model.score(X, y)

print("")
print(f"Unified Model R²: {r2:.4f}")
print("Final Coefficients:")
for name, val in zip(X.columns, model.coef_):
    print(f"  {name:10s}: {val:7.3f}")
print(f"  Intercept : {model.intercept_:7.3f}")

print("")
print("Unified Result Table:")
print(df[['particle', 'type', 'mass', 'pred_m', 'error_pct']].round(2))

# Null Hypothesis Test (Random Assignment) - 10,000 trials
print("")
print("Running Permutation Test (10,000 trials)...")
n_trials = 10000
random_r2 = []
for _ in range(n_trials):
    y_rand = np.random.permutation(y)
    random_r2.append(LinearRegression().fit(X, y_rand).score(X, y_rand))

p_value = np.mean(np.array(random_r2) >= r2)
print(f"Final P-Value (N=9): {p_value:.6f}")

# ============================================================================
# STEP 3: FINAL VISUALIZATION
# ============================================================================

out_dir = "KSAU/publish/v2.3/figures/v2_4_final"
os.makedirs(out_dir, exist_ok=True)

plt.figure(figsize=(12, 8))
sns.scatterplot(data=df, x='ln_m', y='pred_ln_m', hue='type', s=300, palette=['blue', 'red'], edgecolors='black')
plt.plot([y.min()-1, y.max()+1], [y.min()-1, y.max()+1], 'k--', alpha=0.5)

for i, txt in enumerate(df['particle']):
    plt.annotate(txt, (df.ln_m[i], df.pred_ln_m[i]), xytext=(10, -5), textcoords='offset points', fontsize=12, fontweight='bold')

plt.title(f"KSAU v2.4 Final Unified Fermion Fit\nN=9, R²={r2:.4f}, p={p_value:.4f}", fontsize=16)
plt.xlabel("ln(Observed Mass [MeV])", fontsize=14)
plt.ylabel("ln(Predicted Mass [MeV])", fontsize=14)
plt.grid(True, alpha=0.3)
plt.savefig(f"{out_dir}/v2.4_final_unified_fit.png", dpi=300)

print("")
print(f"Final Figure saved to {out_dir}/v2.4_final_unified_fit.png")
print("Analysis Complete.")
