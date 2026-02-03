import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from scipy import stats

# Ensure figures directory exists
os.makedirs("figures", exist_ok=True)

print("=== KSAU v2.x Robust Statistical Analysis ===")

# 1. Data Definition
quark_data = {
    "u": {"name": "Up",      "gen": 1, "mass": 2.16,   "Vol": 5.333,  "Nc": 6,  "L": 3, "link": "L6a5",   "type": "Up-type"},
    "d": {"name": "Down",    "gen": 1, "mass": 4.67,   "Vol": 7.328,  "Nc": 6,  "L": 0, "link": "L6a4",   "type": "Down-type"},
    "s": {"name": "Strange", "gen": 2, "mass": 93.4,   "Vol": 9.802,  "Nc": 8,  "L": 1, "link": "L8a16",  "type": "Down-type"},
    "c": {"name": "Charm",   "gen": 2, "mass": 1270.0, "Vol": 10.667, "Nc": 8,  "L": 2, "link": "L8a19",  "type": "Up-type"},
    "b": {"name": "Bottom",  "gen": 3, "mass": 4180.0, "Vol": 12.276, "Nc": 10, "L": 0, "link": "L10a140", "type": "Down-type"},
    "t": {"name": "Top",     "gen": 3, "mass": 172690.,"Vol": 17.862, "Nc": 10, "L": 5, "link": "L10a56",  "type": "Up-type"}
}

df = pd.DataFrame.from_dict(quark_data, orient='index')
df['log_mass'] = np.log(df['mass'])

# Normalize Volume: (V - Vmin) / (Vmax - Vmin)
v_min = df['Vol'].min()
v_max = df['Vol'].max()
df['Vol_norm'] = (df['Vol'] - v_min) / (v_max - v_min)

print("Data Summary (Normalized):")
print(df[['name', 'mass', 'log_mass', 'Vol', 'Vol_norm']])

# 2. Statistical Regression (OLS) with StatsModels for detailed metrics
import statsmodels.api as sm

X = df['Vol_norm']
y = df['log_mass']
X_const = sm.add_constant(X)

model_sm = sm.OLS(y, X_const).fit()

print("\n[Result 1] Regression Statistics")
print(model_sm.summary())

# Extract confidence intervals
conf_int = model_sm.conf_int(alpha=0.05)
conf_int.columns = ['2.5%', '97.5%']
print("\nConfidence Intervals (95%):")
print(conf_int)

# Predictions & Residuals
df['log_mass_pred'] = model_sm.predict(X_const)
df['mass_pred'] = np.exp(df['log_mass_pred'])
df['residuals'] = df['log_mass'] - df['log_mass_pred']

# RMSE
rmse = np.sqrt(mean_squared_error(df['log_mass'], df['log_mass_pred']))
print(f"\nRMSE (Log Space): {rmse:.4f}")

# Cross Validation (Leave-One-Out)
from sklearn.model_selection import LeaveOneOut
loo = LeaveOneOut()
cv_errors = []
for train_index, test_index in loo.split(X):
    X_train, X_test = X.iloc[train_index].values.reshape(-1,1), X.iloc[test_index].values.reshape(-1,1)
    y_train, y_test = y.iloc[train_index], y.iloc[test_index]
    reg = LinearRegression().fit(X_train, y_train)
    y_pred = reg.predict(X_test)
    cv_errors.append((y_pred[0] - y_test.values[0])**2)

rmse_cv = np.sqrt(np.mean(cv_errors))
print(f"RMSE (Leave-One-Out CV): {rmse_cv:.4f}")

# 3. Visualization: Regression with Confidence Bands & Residuals
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Plot 1: Regression Fit
sns.regplot(data=df, x='Vol_norm', y='log_mass', ax=axes[0], ci=95, scatter_kws={'s':100, 'color':'blue'}, line_kws={'color':'red'})
for idx, row in df.iterrows():
    axes[0].text(row['Vol_norm']+0.02, row['log_mass'], row['name'], fontsize=10)
axes[0].set_title(f"Mass vs Normalized Volume\n$R^2={model_sm.rsquared:.3f}, RMSE={rmse:.3f}$")
axes[0].set_xlabel("Normalized Hyperbolic Volume")
axes[0].set_ylabel("ln(Mass / MeV)")

# Plot 2: Residuals
axes[1].axhline(0, color='black', linestyle='--')
sns.scatterplot(data=df, x='Vol_norm', y='residuals', hue='type', s=150, ax=axes[1], palette='viridis')
for idx, row in df.iterrows():
    axes[1].text(row['Vol_norm']+0.02, row['residuals'], row['name'], fontsize=10)
axes[1].set_title("Residual Analysis (Log Space)")
axes[1].set_xlabel("Normalized Hyperbolic Volume")
axes[1].set_ylabel("Residual (Obs - Pred)")
axes[1].set_ylim(-2, 2)

plt.tight_layout()
plt.savefig("figures/v2_stat_analysis.png", dpi=300)
print("\nSaved figure: figures/v2_stat_analysis.png")

print("\n=== Analysis Complete ===")