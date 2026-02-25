
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

data = [
    {"name": "Strange", "tau": 1.238e-08, "n": 11.0, "u": 0.0, "s": 4.0},
    {"name": "Charm", "tau": 1.04e-12, "n": 11.0, "u": 0.0, "s": -5.0},
    {"name": "Bottom", "tau": 1.638e-12, "n": 11.0, "u": 0.0, "s": -2.0},
    {"name": "Top", "tau": 4.67e-25, "n": 11.0, "u": 0.0, "s": -3.0},
    {"name": "Muon", "tau": 2.19698e-06, "n": 4.0, "u": 1.0, "s": 0.0},
    {"name": "Tau", "tau": 2.903e-13, "n": 6.0, "u": 1.0, "s": 0.0},
    {"name": "W", "tau": 3.16e-25, "n": 11.0, "u": 0.0, "s": 0.0},
    {"name": "Z", "tau": 2.64e-25, "n": 11.0, "u": 0.0, "s": -2.0},
    {"name": "Higgs", "tau": 1.62e-22, "n": 11.0, "u": 0.0, "s": -1.0},
]

df = pd.DataFrame(data)
df['ln_gamma'] = -np.log(df['tau'])
df['tsi_sum'] = df['n'] + df['u'] + np.abs(df['s'])
df['tsi_prod'] = (df['n'] * df['u']) / np.where(np.abs(df['s'])==0, 1e-9, np.abs(df['s'])) # dummy to avoid div 0

# Test original 6 from Cycle 10: Muon, Tau, Top, W, Z, Higgs
orig_6_names = ["Muon", "Tau", "Top", "W", "Z", "Higgs"]
df6 = df[df['name'].isin(orig_6_names)]

X6 = df6[['tsi_sum']].values
y6 = df6['ln_gamma'].values
reg6 = LinearRegression().fit(X6, y6)
print(f"Original 6 (Sum Formula) R2: {reg6.score(X6, y6)}")

X6p = df6[['tsi_prod']].values
reg6p = LinearRegression().fit(X6p, y6)
print(f"Original 6 (Prod Formula) R2: {reg6p.score(X6p, y6)}")
