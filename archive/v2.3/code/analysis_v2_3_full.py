import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from scipy.optimize import minimize
import os

# Setup
os.makedirs("KSAU/publish/v2.3/figures", exist_ok=True)
data_path = "KSAU/publish/v2.3/data/quark_data_v2.3.csv"

print("=== KSAU v2.3 Full Analysis ===")

# 1. Load Data
df = pd.read_csv(data_path)
df['log_mass'] = np.log(df['mass_mev'])
print("Data Loaded:")
print(df[['name', 'mass_mev', 'hyperbolic_vol', 'linking_number_tot', 'signature']])

# 2. Mass Regression (Full Model)
# ln(m) = alpha*Vol + beta*L + gamma*Sig + C
X = df[['hyperbolic_vol', 'linking_number_tot', 'signature']]
y = df['log_mass']

model = LinearRegression().fit(X, y)
df['log_mass_pred'] = model.predict(X)
df['mass_pred'] = np.exp(df['log_mass_pred'])
df['error_%'] = (df['mass_pred'] - df['mass_mev']) / df['mass_mev'] * 100

r2 = model.score(X, y)
print(f"\n[Mass Prediction Results (R^2 = {r2:.4f})]")
print(f"Formula: ln(m) = {model.coef_[0]:.3f}*Vol + {model.coef_[1]:.3f}*L + {model.coef_[2]:.3f}*Sig + {model.intercept_:.3f}")
print(df[['name', 'mass_mev', 'mass_pred', 'error_%']].round(2))

# Plot Mass Fit
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='hyperbolic_vol', y='log_mass', hue='type', style='generation', s=200, palette='viridis')
# Add predicted points
plt.scatter(df['hyperbolic_vol'], df['log_mass_pred'], color='red', marker='x', s=100, label='Predicted')

for i in range(len(df)):
    plt.plot([df.iloc[i]['hyperbolic_vol'], df.iloc[i]['hyperbolic_vol']], 
             [df.iloc[i]['log_mass'], df.iloc[i]['log_mass_pred']], 'r--', alpha=0.5)
    plt.text(df.iloc[i]['hyperbolic_vol']+0.2, df.iloc[i]['log_mass'], df.iloc[i]['name'])

plt.title(f"KSAU v2.3 Mass Formula\n$R^2={r2:.3f}$ (Vol + L + Sig)")
plt.xlabel("Hyperbolic Volume")
plt.ylabel("ln(Mass / MeV)")
plt.legend()
plt.tight_layout()
plt.savefig("KSAU/publish/v2.3/figures/v2.3_mass_fit.png", dpi=300)
print("\nSaved Mass Fit Figure.")


# 3. CKM Optimization
print("\n[CKM Matrix Optimization]")
# Experimental CKM (Magnitude)
ckm_exp = np.array([
    [0.974, 0.224, 0.004],
    [0.218, 0.997, 0.041],
    [0.009, 0.041, 0.999]
])

# Define quarks for loops
up_quarks = df[df['type']=='Up-type'].sort_values('generation').reset_index(drop=True)
down_quarks = df[df['type']=='Down-type'].sort_values('generation').reset_index(drop=True)

# Optimization Function
def ckm_cost(params):
    # params: [k, w_vol, w_gen, w_sig]
    k, w_vol, w_gen, w_sig = params
    error = 0
    
    for i, u in up_quarks.iterrows():
        for j, d in down_quarks.iterrows():
            # Distance Metric v2.3
            # dVol = abs(Vu - Vd)
            # dGen = abs(Gu - Gd)
            # dSig = abs(Su - Sd)
            
            # Note: Using Volume difference as structural barrier instead of Nc
            # Nc was derived from Crossing Number which correlates with Volume
            d_vol = abs(u['hyperbolic_vol'] - d['hyperbolic_vol'])
            d_gen = abs(u['generation'] - d['generation'])
            d_sig = abs(u['signature'] - d['signature'])
            
            # Distance function
            dist = w_vol * d_vol + w_gen * (d_gen ** 3) + w_sig * d_sig
            pred = np.exp(-k * dist)
            
            # Squared error (weighted for small elements)
            weight = 1.0
            if ckm_exp[i,j] < 0.01: weight = 10.0
            error += weight * (pred - ckm_exp[i,j])**2
            
    return error

# Initial guess
initial_guess = [0.1, 0.5, 1.0, 0.1]
bounds = [(0, 2), (0, 2), (0, 5), (0, 2)]

result = minimize(ckm_cost, initial_guess, bounds=bounds, method='L-BFGS-B')

print("Optimization Success:", result.success)
print("Best Params [k, w_vol, w_gen, w_sig]:", result.x.round(4))

# Generate Best CKM
best_k, best_wv, best_wg, best_ws = result.x
ckm_pred = np.zeros((3,3))

for i, u in up_quarks.iterrows():
    for j, d in down_quarks.iterrows():
        d_vol = abs(u['hyperbolic_vol'] - d['hyperbolic_vol'])
        d_gen = abs(u['generation'] - d['generation'])
        d_sig = abs(u['signature'] - d['signature'])
        
        dist = best_wv * d_vol + best_wg * (d_gen ** 3) + best_ws * d_sig
        ckm_pred[i, j] = np.exp(-best_k * dist)

print("\nPredicted CKM:")
print(ckm_pred.round(4))
print("\nExperimental CKM:")
print(ckm_exp)

# Plot CKM
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
sns.heatmap(ckm_pred, annot=True, fmt=".4f", cmap="Blues", ax=ax1, vmin=0, vmax=1)
ax1.set_title("KSAU v2.3 Predicted |V_ij|")
ax1.set_xticklabels(['d', 's', 'b'])
ax1.set_yticklabels(['u', 'c', 't'])

sns.heatmap(ckm_exp, annot=True, fmt=".4f", cmap="Greens", ax=ax2, vmin=0, vmax=1)
ax2.set_title("Experimental |V_ij|")
ax2.set_xticklabels(['d', 's', 'b'])
ax2.set_yticklabels(['u', 'c', 't'])

plt.tight_layout()
plt.savefig("KSAU/publish/v2.3/figures/v2.3_ckm_matrix.png", dpi=300)
print("Saved CKM Figure.")