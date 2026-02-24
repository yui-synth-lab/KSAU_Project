import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

data = [
    {"name": "Electron", "n": 12, "N": 3, "D": 3, "C": 1, "G": 1, "B": 0},
    {"name": "Muon",     "n": 31, "N": 4, "D": 5, "C": 1, "G": 2, "B": 0},
    {"name": "Tau",      "n": 41, "N": 6, "D": 9, "C": 1, "G": 3, "B": 0},
    {"name": "Up",       "n": 15, "N": 9, "D": 12, "C": 2, "G": 1, "B": 0},
    {"name": "Down",     "n": 17, "N": 8, "D": 20, "C": 3, "G": 1, "B": 0},
    {"name": "Strange",  "n": 27, "N": 11, "D": 36, "C": 3, "G": 2, "B": 0},
    {"name": "Charm",    "n": 36, "N": 11, "D": 70, "C": 2, "G": 2, "B": 0},
    {"name": "Bottom",   "n": 39, "N": 11, "D": 96, "C": 3, "G": 3, "B": 0},
    {"name": "Top",      "n": 53, "N": 11, "D": 110, "C": 2, "G": 3, "B": 0},
    {"name": "W",        "n": 50, "N": 11, "D": 64, "C": 3, "G": 4, "B": 1},
    {"name": "Z",        "n": 50, "N": 11, "D": 112, "C": 3, "G": 4, "B": 1},
    {"name": "Higgs",    "n": 51, "N": 11, "D": 136, "C": 2, "G": 4, "B": 1},
]

df = pd.DataFrame(data)
df["lnD"] = np.log(df["D"])

cols = ["N", "lnD", "C", "G", "B"]
X = df[cols]
y = df["n"]

model = LinearRegression()
model.fit(X, y)

print("Coefficients:")
for col, coef in zip(cols, model.coef_):
    print(f"  {col}: {coef:.4f}")
print(f"Intercept: {model.intercept_:.4f}")
print(f"R^2: {model.score(X, y):.4f}")

df["n_pred"] = model.predict(X)
df["diff"] = df["n"] - df["n_pred"]
print("\nPredictions vs Actual:")
print(df[["name", "n", "n_pred", "diff"]].to_string())
