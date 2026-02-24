import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import LinearRegression

# SSoT Loader Setup
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
ssot_path = project_root / "ssot"
sys.path.insert(0, str(ssot_path))
from ksau_ssot import SSOT

def main():
    ssot = SSOT()
    consts = ssot.constants()
    params = ssot.parameters()
    topologies = ssot.topology_assignments()

    pi = consts["mathematical_constants"]["pi"]
    kappa = consts["mathematical_constants"]["kappa"]
    delta_c = pi / 12
    
    particles = []
    for sector in ["leptons", "quarks", "bosons"]:
        for name, data in params.get(sector, {}).items():
            if name in topologies:
                particles.append({
                    "name": name,
                    "sector": sector,
                    "mass": data["observed_mass_mev"],
                    "v": topologies[name]["volume"],
                    "N": topologies[name].get("crossing_number", 0),
                    "D": topologies[name].get("determinant", 1),
                    "C": topologies[name].get("components", 1),
                    "G": topologies[name].get("generation", 4),
                    "B": 1 if topologies[name].get("is_brunnian", False) else 0
                })
    
    df = pd.DataFrame(particles)
    df["ln_m"] = np.log(df["mass"])
    df["lnD"] = np.log(df["D"])

    # Ideal n: n = (ln_m - kappa*v - C_glob) / delta_c
    # We'll optimize C_glob to make n as close to integers as possible
    best_var = 1e10
    best_c = 0
    for c in np.linspace(-10, 10, 2001):
        n_exact = (df["ln_m"] - kappa * df["v"] - c) / delta_c
        var = np.mean((n_exact - np.round(n_exact))**2)
        if var < best_var:
            best_var = var
            best_c = c
            
    df["n_exact"] = (df["ln_m"] - kappa * df["v"] - best_c) / delta_c
    df["n_int"] = np.round(df["n_exact"]).astype(int)
    
    # Regression: n_int ~ N, D, C, G, B, lnD, v
    features = ["N", "D", "C", "G", "B", "lnD", "v"]
    X = df[features]
    y = df["n_int"]
    
    model = LinearRegression()
    model.fit(X, y)
    
    r2 = model.score(X, y)
    print(f"Regression R^2: {r2:.6f}")
    
    df["n_rule"] = np.round(model.predict(X)).astype(int)
    
    # Evaluate MAE with n_rule
    df["ln_m_pred"] = kappa * df["v"] + best_c + df["n_rule"] * delta_c
    df["err_pct"] = np.abs(np.exp(df["ln_m_pred"] - df["ln_m"]) - 1) * 100
    mae_pct = np.mean(df["err_pct"])
    
    print(f"MAE (%) with rule: {mae_pct:.6f}%")
    
    if mae_pct < 0.1:
        print("SUCCESS! Formula found.")
        print("Coefficients:")
        for f, c in zip(features, model.coef_):
            print(f"  {f}: {c:.4f}")
        print(f"Intercept: {model.intercept_:.4f}")

    results = {
        "iteration": 4,
        "hypothesis_id": "H23",
        "task_name": "Full invariant regression for n",
        "computed_values": {
            "r2_regression": float(r2),
            "mae_pct": float(mae_pct),
            "c_glob": float(best_c)
        },
        "formula": {
            "features": features,
            "coefs": [float(c) for c in model.coef_],
            "intercept": float(model.intercept_)
        },
        "particle_details": df.to_dict(orient="records")
    }
    
    with open(current_file.parents[1] / "results_regression.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
